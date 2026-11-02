"""Summarize a staggered FL job from its server log and check that no agent trained more sites than allowed.

Usage: python stagger_report.py <server-log-file>

Reads the `STAGGER {json}` lines that StaggeredFedAvg and StaggeredScatterAndGather write, and prints per round: duration, sites that
succeeded or failed, and the most sites any agent trained at once next to its limit. Exits with 1 when an agent went
over its limit or the job failed, so it can also gate an automated test.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

STAGGER_LINE = re.compile(r"STAGGER (\{.*\})\s*$")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    events = read_events(Path(sys.argv[1]))
    if not events:
        print("No STAGGER lines found: is this the server log of a job that uses a staggered controller?")
        return 1
    problems = report(events)
    for problem in problems:
        print(f"PROBLEM: {problem}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def read_events(log_path: Path) -> list[dict[str, Any]]:
    events = []
    for line in log_path.read_text(errors="replace").splitlines():
        match = STAGGER_LINE.search(line)
        if match:
            events.append(json.loads(match.group(1)))
    return events


def report(events: list[dict[str, Any]]) -> list[str]:
    """Print one line per round and return every problem found."""
    problems = []
    limits: dict[str, int] = {}
    agent_of: dict[str, str] = {}
    in_flight: dict[str, int] = {}
    peak: dict[str, int] = {}
    for event in events:
        kind, round_number = event["event"], event.get("round")
        if kind == "round_start":
            limits = {agent: info["max_concurrent"] for agent, info in event["agents"].items()}
            agent_of = {name: agent for agent, info in event["agents"].items() for name in info["clients"]}
            in_flight = {agent: 0 for agent in limits}
            peak = dict(in_flight)
        elif kind == "task_scheduled":
            agent = agent_of[event["client"]]
            in_flight[agent] += 1
            peak[agent] = max(peak[agent], in_flight[agent])
            if in_flight[agent] > limits[agent]:
                problems.append(
                    f"round {round_number}: agent {agent} had {in_flight[agent]} sites training, limit {limits[agent]}"
                )
        elif kind == "task_done":
            in_flight[agent_of[event["client"]]] -= 1
        elif kind == "round_done":
            print(_round_line(round_number, event, peak, limits))
        elif kind == "job_failed":
            problems.append(f"round {round_number}: job failed ({event['reason']}); failed sites: {event.get('failed')}")
    return problems


def _round_line(round_number: int, event: dict[str, Any], peak: dict[str, int], limits: dict[str, int]) -> str:
    agents = ", ".join(f"{agent} {peak[agent]}/{limits[agent]}" for agent in sorted(limits))
    failed = ", ".join(f"{name} ({reason})" for name, reason in event["failed"].items()) or "none"
    return (
        f"round {round_number}: {event['duration_s']:.0f} s, {event['succeeded']} succeeded, failed: {failed}; "
        f"most training at once per agent (peak/limit): {agents}"
    )


if __name__ == "__main__":
    sys.exit(main())
