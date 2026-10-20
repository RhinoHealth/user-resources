"""ScatterAndGather that limits how many sites train at the same time on each shared GPU agent.

Copy this file unchanged into your job's `app/custom/` and point `config_fed_server.json` at
`staggered_scatter_and_gather.StaggeredScatterAndGather`. Every option is documented on the class.

Each round, every site gets the same global model, as in ScatterAndGather. The difference is when: sites are grouped
by the agent (machine) they run on, and each agent trains at most `max_concurrent` of its sites at once. The rest
wait in a per-agent queue until a slot frees. Aggregation, persistence and model selection are ScatterAndGather's own.

Every scheduling event is logged as one `STAGGER {json}` line (see `stagger_report.py`). Site and job failures are
also logged as plain sentences, so a failed run explains itself in the server log.
"""

import json
import re
import threading
import time
from collections import deque
from typing import Any, Callable, Optional

from nvflare.apis.client import Client
from nvflare.apis.controller_spec import ClientTask, Task, TaskCompletionStatus
from nvflare.apis.fl_constant import ReturnCode
from nvflare.apis.fl_context import FLContext
from nvflare.apis.shareable import Shareable
from nvflare.apis.signal import Signal
from nvflare.app_common.workflows.scatter_and_gather import ScatterAndGather

BATCH = "batch"
SLIDING = "sliding"
DEFAULT_AGENT_NAME_PATTERN = r"_\d+$"
TROUBLESHOOTING_HINT = "See 'Troubleshooting' in the staggered FL guide."


class StaggeredScatterAndGather(ScatterAndGather):
    """ScatterAndGather that trains at most `max_concurrent` sites per agent at a time within each round.

    Args:
        max_concurrent: sites of one agent that may train at the same time (K). Size it so K training sites plus
            every waiting site's CUDA context fit in the GPU.
        agent_max_concurrent: per-agent overrides of `max_concurrent`, keyed by agent name.
        wave_mode: "sliding" starts the next waiting site as soon as any slot frees; "batch" waits for the agent's
            whole wave to finish before starting the next one.
        max_retries: times a failed site is retried in the same round. A site whose training process crashed does
            not come back, so 0 is the safe default.
        min_successful_clients: sites that must succeed for a round to count. Defaults to `min_clients`. Set
            `min_clients` to the number of sites in the job, so the platform starts it with every site, and this
            lower, so one failed site doesn't stop the job for everyone.
        exclude_failed_clients: stop scheduling a site after it fails, for the rest of the job, instead of waiting
            up to `train_timeout` for it every round.
        agent_name_pattern: regex removed from a site name to get its agent name; sites with the same result share
            one GPU agent. The default turns `my_agent_3` into `my_agent`.
        wait_for_clients_timeout: seconds the first round waits for `min_clients` sites to connect.
        **kwargs: ScatterAndGather arguments. `train_timeout` applies per site task, counted from when that site's
            task is scheduled, so size it for one site's local training, not the whole round.
    """

    def __init__(
        self,
        max_concurrent: int = 2,
        agent_max_concurrent: Optional[dict[str, int]] = None,
        wave_mode: str = BATCH,
        max_retries: int = 0,
        min_successful_clients: Optional[int] = None,
        exclude_failed_clients: bool = True,
        agent_name_pattern: str = DEFAULT_AGENT_NAME_PATTERN,
        wait_for_clients_timeout: float = 300.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if max_concurrent < 1:
            raise ValueError(f"max_concurrent must be >= 1, got {max_concurrent}")
        for agent, limit in (agent_max_concurrent or {}).items():
            if limit < 1:
                raise ValueError(f"agent_max_concurrent[{agent!r}] must be >= 1, got {limit}")
        if wave_mode not in (BATCH, SLIDING):
            raise ValueError(f"wave_mode must be '{BATCH}' or '{SLIDING}', got {wave_mode!r}")
        if max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {max_retries}")
        if min_successful_clients is not None and not 1 <= min_successful_clients <= self._min_clients:
            raise ValueError(
                f"min_successful_clients must be between 1 and min_clients ({self._min_clients}), "
                f"got {min_successful_clients}"
            )
        self._max_concurrent = max_concurrent
        self._agent_max_concurrent = dict(agent_max_concurrent or {})
        self._wave_mode = wave_mode
        self._max_retries = max_retries
        self._min_successful_clients = min_successful_clients or self._min_clients
        self._exclude_failed_clients = exclude_failed_clients
        self._agent_name_pattern = re.compile(agent_name_pattern)
        self._wait_for_clients_timeout = wait_for_clients_timeout
        # Sites in the job (taken in the first round) and sites dropped from it, with the reason.
        self._job_sites: Optional[list[str]] = None
        self._excluded: dict[str, str] = {}
        # Written by result callbacks on NVFlare's threads, read by the round loop.
        self._lock = threading.Lock()
        self._succeeded: set[str] = set()
        self._error_results: dict[str, str] = {}

    def broadcast_and_wait(
        self,
        task: Task,
        fl_ctx: FLContext,
        targets=None,
        min_responses: int = 1,
        wait_time_after_min_received: int = 0,
        abort_signal: Optional[Signal] = None,
    ):
        # ScatterAndGather's round loop calls this once per round with the train task; only that call is staggered.
        if task.name != self.train_task_name:
            return super().broadcast_and_wait(
                task, fl_ctx, targets, min_responses, wait_time_after_min_received, abort_signal
            )
        self._run_staggered_round(task.data, fl_ctx, abort_signal)

    def process_result_of_unknown_task(
        self, client: Client, task_name, client_task_id, result: Shareable, fl_ctx: FLContext
    ) -> None:
        # A result that arrives after its task timed out may race its retry; keep only the retry's.
        self._log_event(fl_ctx, "late_result_ignored", client=client.name, task=task_name)

    def _run_staggered_round(self, data: Shareable, fl_ctx: FLContext, abort_signal: Optional[Signal]) -> None:
        sites = self._sites_for_round(fl_ctx, abort_signal)
        if sites is None:
            return
        if len(sites) < self._min_successful_clients:
            self._stop_job(fl_ctx, succeeded=0, failed=dict(self._excluded))
            return

        round_state = _StaggeredRound(sites, self._agent_of, self._limit_of)
        with self._lock:
            self._succeeded = set()
            self._error_results = {}
        self._log_event(
            fl_ctx,
            "round_start",
            clients=sites,
            excluded=sorted(self._excluded),
            agents={
                agent: {"clients": list(queue), "max_concurrent": round_state.limits[agent]}
                for agent, queue in round_state.pending.items()
            },
            wave_mode=self._wave_mode,
            min_successful_clients=self._min_successful_clients,
        )

        while round_state.has_work():
            if abort_signal and abort_signal.triggered:
                self.cancel_all_tasks(fl_ctx=fl_ctx)
                self._log_event(fl_ctx, "round_aborted")
                return
            self._collect_finished_tasks(round_state, fl_ctx)
            # Stop as soon as the round can no longer reach min_successful_clients, instead of training the rest.
            if self._num_succeeded() + round_state.num_remaining() < self._min_successful_clients:
                self.cancel_all_tasks(fl_ctx=fl_ctx)
                self._stop_job(fl_ctx, succeeded=self._num_succeeded(), failed=round_state.failed)
                return
            self._schedule_waiting_sites(round_state, data, fl_ctx)
            time.sleep(self._task_check_period)

        self._finish_round(round_state, fl_ctx)

    def _sites_for_round(self, fl_ctx: FLContext, abort_signal: Optional[Signal]) -> Optional[list[str]]:
        """Sites to train this round: every connected job site that hasn't been excluded."""
        if self._job_sites is None:
            self._job_sites = self._wait_for_clients(fl_ctx, abort_signal)
            if self._job_sites is None:
                return None
            self._warn_if_nothing_to_stagger(fl_ctx)
        connected = {client.name for client in self._engine.get_clients()}
        for name in self._job_sites:
            if name not in connected and name not in self._excluded:
                self._excluded[name] = "site disconnected from the job"
                self._log_site_failed(fl_ctx, name, self._excluded[name], excluded=True, sites_left=None)
        return [name for name in self._job_sites if name not in self._excluded]

    def _wait_for_clients(self, fl_ctx: FLContext, abort_signal: Optional[Signal]) -> Optional[list[str]]:
        # The job can start before every site has registered; training a partial set would leave sites out.
        deadline = time.time() + self._wait_for_clients_timeout
        while True:
            names = sorted(client.name for client in self._engine.get_clients())
            if len(names) >= self._min_clients:
                return names
            if (abort_signal and abort_signal.triggered) or time.time() >= deadline:
                break
            time.sleep(self._task_check_period)
        message = (
            f"Job stopped before training: only {len(names)} of min_clients={self._min_clients} sites connected "
            f"within {self._wait_for_clients_timeout:.0f} s (connected: {', '.join(names) or 'none'}). "
            f"Set min_clients to the number of sites in the job. {TROUBLESHOOTING_HINT}"
        )
        self.log_error(fl_ctx, message)
        self._log_event(fl_ctx, "job_failed", reason="not_enough_clients", connected=names)
        self.system_panic(message, fl_ctx)
        return None

    def _warn_if_nothing_to_stagger(self, fl_ctx: FLContext) -> None:
        sites_per_agent: dict[str, int] = {}
        for name in self._job_sites:
            agent = self._agent_of(name)
            sites_per_agent[agent] = sites_per_agent.get(agent, 0) + 1
        if all(count <= self._limit_of(agent) for agent, count in sites_per_agent.items()):
            self.log_warning(
                fl_ctx,
                f"No agent has more sites than its max_concurrent, so no site ever waits and staggering has no "
                f"effect. Sites per agent: {sites_per_agent}. If these sites share one GPU agent, check "
                f"agent_name_pattern ({self._agent_name_pattern.pattern!r}).",
            )

    def _collect_finished_tasks(self, round_state: "_StaggeredRound", fl_ctx: FLContext) -> None:
        for name in round_state.finished_sites():
            status = round_state.finish(name)
            with self._lock:
                succeeded = name in self._succeeded
                error_result = self._error_results.get(name)
            self._log_event(
                fl_ctx,
                "task_done",
                client=name,
                status=status.value,
                succeeded=succeeded,
                train_s=round_state.train_seconds[name],
            )
            if succeeded:
                continue
            if round_state.attempts[name] <= self._max_retries:
                round_state.requeue(name)
                self._log_event(fl_ctx, "retry_queued", client=name, attempt=round_state.attempts[name] + 1)
                continue
            reason = error_result or self._describe_status(status)
            round_state.failed[name] = reason
            if self._exclude_failed_clients:
                self._excluded[name] = reason
            self._log_event(fl_ctx, "client_failed", client=name, attempts=round_state.attempts[name], reason=reason)
            self._log_site_failed(
                fl_ctx,
                name,
                reason,
                excluded=self._exclude_failed_clients,
                sites_left=self._num_succeeded() + round_state.num_remaining(),
            )

    def _schedule_waiting_sites(self, round_state: "_StaggeredRound", data: Shareable, fl_ctx: FLContext) -> None:
        for agent, queue in round_state.pending.items():
            agent_in_flight = round_state.in_flight_on(agent)
            # Batch mode: the agent's next wave starts only when its whole current wave is done.
            if self._wave_mode == BATCH and agent_in_flight:
                continue
            while queue and agent_in_flight < round_state.limits[agent]:
                name = queue.popleft()
                round_state.start(name, self._schedule_client_task(name, data, fl_ctx))
                agent_in_flight += 1
                self._log_event(
                    fl_ctx,
                    "task_scheduled",
                    client=name,
                    agent=agent,
                    attempt=round_state.attempts[name],
                    agent_in_flight=agent_in_flight,
                    in_flight=round_state.num_in_flight(),
                )

    def _finish_round(self, round_state: "_StaggeredRound", fl_ctx: FLContext) -> None:
        num_succeeded = self._num_succeeded()
        duration = round(time.time() - round_state.started_at, 1)
        self._log_event(
            fl_ctx,
            "round_done",
            duration_s=duration,
            succeeded=num_succeeded,
            failed=round_state.failed,
            excluded=sorted(self._excluded),
            train_s=round_state.train_seconds,
            max_in_flight=round_state.max_in_flight,
        )
        if num_succeeded < self._min_successful_clients:
            self._stop_job(fl_ctx, succeeded=num_succeeded, failed=round_state.failed)
            return
        self.log_info(
            fl_ctx,
            f"Round {self._current_round}: {num_succeeded} of {len(round_state.attempts)} sites succeeded "
            f"in {duration:.0f} s.",
        )

    def _stop_job(self, fl_ctx: FLContext, succeeded: int, failed: dict[str, str]) -> None:
        failures = "; ".join(f"{name}: {reason}" for name, reason in sorted(failed.items())) or "none"
        message = (
            f"Job stopped in round {self._current_round}: {succeeded} sites succeeded, "
            f"{self._min_successful_clients} required (min_successful_clients). Failed: {failures}. "
            f"{TROUBLESHOOTING_HINT}"
        )
        self.log_error(fl_ctx, message)
        self._log_event(fl_ctx, "job_failed", reason="not_enough_successful_clients", succeeded=succeeded, failed=failed)
        self.system_panic(message, fl_ctx)

    def _log_site_failed(
        self, fl_ctx: FLContext, name: str, reason: str, excluded: bool, sites_left: Optional[int]
    ) -> None:
        outcome = "excluded from the remaining rounds" if excluded else "it will be scheduled again next round"
        left = "" if sites_left is None else f"; {sites_left} sites can still succeed this round"
        self.log_error(
            fl_ctx,
            f"Site {name} failed in round {self._current_round} ({reason}); {outcome}{left}, "
            f"{self._min_successful_clients} required.",
        )

    def _describe_status(self, status: TaskCompletionStatus) -> str:
        if status == TaskCompletionStatus.TIMEOUT:
            return f"no result within train_timeout ({self._train_timeout} s)"
        if status == TaskCompletionStatus.CLIENT_DEAD:
            return "site stopped responding"
        return f"task ended with status '{status.value}'"

    def _schedule_client_task(self, client_name: str, data: Shareable, fl_ctx: FLContext) -> Task:
        task = Task(
            name=self.train_task_name,
            data=data,
            props={},
            timeout=self._train_timeout,
            before_task_sent_cb=self._prepare_train_task_data,
            after_task_sent_cb=self._on_task_sent,
            result_received_cb=self._on_train_result,
        )
        self.broadcast(task=task, fl_ctx=fl_ctx, targets=[client_name], min_responses=1)
        return task

    def _on_task_sent(self, client_task: ClientTask, fl_ctx: FLContext) -> None:
        self._log_event(fl_ctx, "task_sent", client=client_task.client.name)

    def _on_train_result(self, client_task: ClientTask, fl_ctx: FLContext) -> None:
        name = client_task.client.name
        rc = client_task.result.get_return_code()
        if rc and rc != ReturnCode.OK:
            self._log_event(fl_ctx, "result_error", client=name, rc=rc)
            with self._lock:
                self._error_results[name] = _describe_return_code(rc)
            client_task.result = None
            return
        self._log_event(fl_ctx, "result_received", client=name)
        self._process_train_result(client_task, fl_ctx)
        with self._lock:
            self._succeeded.add(name)

    def _num_succeeded(self) -> int:
        with self._lock:
            return len(self._succeeded)

    def _agent_of(self, site_name: str) -> str:
        return self._agent_name_pattern.sub("", site_name)

    def _limit_of(self, agent: str) -> int:
        return self._agent_max_concurrent.get(agent, self._max_concurrent)

    def _log_event(self, fl_ctx: FLContext, event: str, **fields: Any) -> None:
        record = {"event": event, "t": round(time.time(), 3), "round": self._current_round, **fields}
        self.log_info(fl_ctx, "STAGGER " + json.dumps(record))


class _StaggeredRound:
    """One round's per-agent queues, in-flight tasks and per-site bookkeeping."""

    def __init__(self, sites: list[str], agent_of: Callable[[str], str], limit_of: Callable[[str], int]):
        self.agent_of = {name: agent_of(name) for name in sites}
        self.pending: dict[str, deque[str]] = {}
        for name in sites:
            self.pending.setdefault(self.agent_of[name], deque()).append(name)
        self.limits = {agent: limit_of(agent) for agent in self.pending}
        self.in_flight: dict[str, Task] = {}
        self.attempts = {name: 0 for name in sites}
        self.failed: dict[str, str] = {}
        self.train_seconds: dict[str, float] = {}
        self.max_in_flight = {agent: 0 for agent in self.pending}
        self.started_at = time.time()
        self._task_started_at: dict[str, float] = {}

    def has_work(self) -> bool:
        return bool(self.in_flight) or any(self.pending.values())

    def num_in_flight(self) -> int:
        return len(self.in_flight)

    def num_remaining(self) -> int:
        """Sites that may still succeed this round: training now or waiting for a slot."""
        return len(self.in_flight) + sum(len(queue) for queue in self.pending.values())

    def in_flight_on(self, agent: str) -> int:
        return sum(1 for name in self.in_flight if self.agent_of[name] == agent)

    def finished_sites(self) -> list[str]:
        return [name for name, task in self.in_flight.items() if task.completion_status is not None]

    def start(self, name: str, task: Task) -> None:
        self.attempts[name] += 1
        self.in_flight[name] = task
        self._task_started_at[name] = time.time()
        agent = self.agent_of[name]
        self.max_in_flight[agent] = max(self.max_in_flight[agent], self.in_flight_on(agent))

    def finish(self, name: str) -> TaskCompletionStatus:
        self.train_seconds[name] = round(time.time() - self._task_started_at[name], 1)
        return self.in_flight.pop(name).completion_status

    def requeue(self, name: str) -> None:
        self.pending[self.agent_of[name]].append(name)


def _describe_return_code(rc: str) -> str:
    if rc in (ReturnCode.EXECUTION_EXCEPTION, ReturnCode.TASK_ABORTED):
        return f"the site's training process failed or exited ({rc}); see the site's log"
    return f"site returned error '{rc}'"
