# Staggered Federated Learning on a Shared GPU
> Last validated: pending (validation on FCP is in progress)

## Description
Several sites (workgroups) can run their federated learning clients on the **same GPU agent**. With NVFlare's
standard `ScatterAndGather`, every site trains at the same time in each round, so the GPU needs memory for all of them
at once: 8 sites of a 2.7 GB model need ~22 GB, and a ninth site doesn't fit.

**Staggering** lets those sites take turns. A drop-in replacement for `ScatterAndGather`,
`StaggeredScatterAndGather`, trains at most **K** sites of each agent at a time; the rest wait in a queue and start
as soon as a slot frees. Every site still trains on the same global model in every round, and aggregation is
unchanged, so the result is the same federated model.

This folder holds the guide (this file), a log report tool, and reference examples you can copy from.

## Resources
- `lightning-chemprop/scatter-and-gather` - Reference example with a PyTorch Lightning model (Chemprop, molecule
  classification) and the `ScatterAndGather` workflow. Start here; its README walks through running it on FCP
- `README.md` - This guide: the concept, the settings you must choose, measured results, monitoring, failures and limits
- `stagger_report.py` - Reads a job's server log and prints, per round, the duration, failed sites and the most sites
  that trained at once on each agent; exits with 1 if an agent went over its limit or the job failed

## How staggering works
- **Agents.** Sites are grouped by the GPU agent (machine) they run on. FCP names each site after its agent plus an
  index (e.g. `my_gpu_agent_1`, `my_gpu_agent_2`), and the controller strips the index to find the agent
  (`agent_name_pattern`, default `_\d+$`).
- **K.** Each agent trains at most `max_concurrent` (K) of its sites at the same time. Agents don't share slots, so
  sites on different agents never wait for each other.
- **Waves.** With N sites on an agent, a round runs in about ⌈N ÷ K⌉ waves. In `sliding` mode (recommended) a waiting
  site starts the moment any slot frees; in `batch` mode the next K start only when the whole current wave is done.
- **A round** ends when every site has finished or failed. Then the server aggregates, saves the global model, and
  starts the next round, exactly as `ScatterAndGather` does.

```
N = 8 sites on one agent, K = 4, sliding
slot 1  |site 1 ====|site 5 ====|
slot 2  |site 2 ======|site 6 ===|
slot 3  |site 3 ===|site 7 ======|
slot 4  |site 4 =====|site 8 ====|
        round start          aggregate -> next round
```

## When to use it
Use it when several sites share one GPU agent and running all of them at once would not fit in GPU memory, or would
leave too little memory for safety. If all sites fit comfortably, plain `ScatterAndGather` (everyone at once) is
faster, as long as the agent's CPU keeps up (see "Measured results").

## Adapting your own model
Copy what the reference example does; the lines that matter are marked `# Staggering:` in its code and its configs.

1. **Server workflow.** Copy `staggered_scatter_and_gather.py` unchanged into your job's `app/custom/`, and in
   `config_fed_server.json` replace the `ScatterAndGather` path with
   `staggered_scatter_and_gather.StaggeredScatterAndGather`, adding the settings in the next section.
2. **One process per site** (`"launch_once": true` on the `SubprocessLauncher` in `config_fed_client.json`), with the
   training script looping over rounds:
   ```python
   while flare.is_running():
       input_model = flare.receive()   # a waiting site sits here until its turn
       ...train...
       flare.send(output_model)         # Lightning: the patched trainer sends for you
   ```
3. **Free the GPU between turns.** A waiting site should hold only its CUDA context (~0.3 GB).
   - **PyTorch Lightning** with `flare.patch(trainer)`: nothing to do; the patch moves the model to the CPU after each
     round.
   - **Plain PyTorch:** at the end of each round, after copying the weights to the CPU for `flare.send`, drop every GPU
     tensor and release the cache:
     ```python
     params = {k: v.cpu() for k, v in model.state_dict().items()}
     del model, optimizer
     gc.collect()
     torch.cuda.empty_cache()
     ```
   - **Keep the data on the CPU** between rounds and move each batch to the GPU during training (the normal data
     loader pattern). Data you preload onto the GPU stays there while the site waits, and lowers the K that fits.
4. **End the process on any error.** Wrap the entry point so an exception prints the traceback and exits at once with
   `os._exit(1)` (see the example). With a plain `raise`, NVFlare's background threads keep the process alive but
   silent; the site then only counts as failed after `heartbeat_timeout` (10 minutes in the example), holding a slot
   the whole time.
5. **GPU access.** Set `NVIDIA_VISIBLE_DEVICES=all` and `NVIDIA_DRIVER_CAPABILITIES=compute,utility` in the image:
   FL client pods don't request a GPU, so without these the container sees none and trains on the CPU.

## Settings you must decide
All are in `config_fed_server.json` under the workflow's `args`, except `launch_once`, the client timeouts (both in
`config_fed_client.json`) and `timeout_seconds` (in the training run you start from the SDK).

| Setting | Required? | What to set                                                                                    |
|---|---|------------------------------------------------------------------------------------------------|
| `min_clients` | **required** | The number of sites (datasets) in the job. FCP starts the job only when this many sites are up |
| `max_concurrent` (K) | optional, default 2 | See "Choosing K"                                                                               |
| `wave_mode` | optional, default `"batch"` | `"sliding"`: faster, same memory                                                               |
| `min_successful_clients` | optional, default `min_clients` | Sites that must succeed for a round to count. See "Failures"                                   |
| `exclude_failed_clients` | optional, default `true` | Skip a failed site for the rest of the job                                                     |
| `max_retries` | optional, default 0 | Keep 0: a site whose process crashed does not come back                                        |
| `train_timeout` | optional, default 0 (no limit): **set it** | See "Timeouts"                                                                                 |
| `agent_max_concurrent` | optional, default `{}` | A different K per agent, e.g. `{"gpu_agent_a": 4, "gpu_agent_b": 2}`                           |
| `agent_name_pattern` | optional, default `"_\\d+$"` | Only if your site names don't end in `_<number>`                                               |
| `wait_for_clients_timeout` | optional, default 300 | Seconds the first round waits for `min_clients` sites to connect                               |
| `launch_once` (client) | default `true` | See "One process per site, or one per round"                                                   |

### Choosing K
- **GPU memory:** K × (one site's training memory) + (N − K) × 0.3 GB must stay under ~90% of the GPU. Measure one
  site's peak with `nvidia-smi` while a single site trains (K = 1).
- **CPU:** each training site needs CPU too (the small Lightning model below used ~2 cores per training site). When
  the agent's CPU is saturated, a higher K stops helping.
- **Diminishing returns:** once the GPU is busy, more sites at once just make each one slower. In the measurements
  below the gain flattened around K = 4.
- **No overcommit protection:** a K that is too high runs out of GPU memory; nothing checks this for you.

### One process per site, or one per round
| | One process per site (`launch_once: true`, default) | New process per round (`launch_once: false`) |
|---|---|---|
| GPU memory per waiting site | the CUDA context (~0.3 GB), only if your script frees its model and tensors after each round | 0 |
| Overhead per site per turn | lower: Python and your imports start once per job | higher: Python and your imports start every turn |
| State between rounds (optimizer, LR schedule, epoch count) | kept in memory | lost unless your script saves and reloads it |
| Use when | almost always | many sites per GPU, where ~0.3 GB each adds up (30 sites ≈ 9 GB), or a script that can't free its GPU memory between rounds |

### Timeouts
- **`train_timeout`** (server): seconds one site may train, counted from when **its turn** starts, not from the start
  of the round. Use about 1.5 × one site's local training time plus process start-up. With no limit, a site that
  hangs holds its slot forever.
- **`timeout_seconds`** (the training run, in the SDK): FCP stops the whole job after this long, and staggering makes
  jobs longer. Use `num_rounds × ⌈N ÷ K⌉ × (local training time + overhead) × 1.3`; the example notebook computes it.
- **Client timeouts** (`config_fed_client.json`): `external_pre_init_timeout` (start-up of the training process) and
  `heartbeat_timeout` (how long without a heartbeat before the process counts as gone) at 600 s; long training steps
  can delay heartbeats, so keep it high. `peer_read_timeout` at 30 s.
- **Keep rounds short:** a few epochs per round rather than one long round. `train_timeout` stays small, a failure
  costs less, and the sites' models drift apart less.

## Measured results
Measured on one FCP GPU agent with an NVIDIA L4 (23 GB), NVFlare 2.8.1, 8 sites, sliding mode. Two models: a **small
PyTorch Lightning model** (~0.5 GB per training site, ~65 s of training per site per round) and a **mid-size CNN**
(~2.7 GB per training site, ~50 s per site per round).

**Round time by K** (one process per round):

| Sites training at once | Small Lightning model | Mid-size CNN |
|---|---|---|
| 1 | 692 s (1.0×), 0.5 GB, ~2 CPU cores | 623 s (1.0×), 2.7 GB |
| 2 | — | ~337 s (1.9×), 5.5 GB (batch mode) |
| 4 | 195 s (**3.5×**), 2.1 GB, ~7 cores | ~216 s (**2.9×**), 10.9 GB |
| 6 | — | ~212 s (2.9×), 16.3 GB: no faster than K = 4 |
| all 8 (no staggering) | 127 s (5.4×), 4.1 GB, 13 cores (82% CPU) | ~173 s (3.6×), 21.7 GB (94% of the GPU) |

**One process per site vs one per round** (K = 4):

| | Small Lightning model | Mid-size CNN |
|---|---|---|
| Round time | 176–178 s vs 195 s (~10% faster) | 200–204 s vs 216–220 s (~7% faster) |
| Overhead per site per turn | ~8–10 s vs ~20 s | ~22 s vs ~25 s |
| Peak GPU memory | 3.2 GB vs 2.1 GB (+0.3 GB per waiting site) | 12.1 GB vs 10.9 GB |
| State between rounds | kept (epochs continue 50 → 100 → 150) | kept if the script keeps it |

**Scale:** 30 sites on one agent at K = 4 ran at the same ~28 s per site per round as 8 sites, with the same peak GPU
memory (10.9 GB): round time grows linearly with N, memory does not.

**Overhead** is the time a slot is not training between two sites: sending the global model to the next site,
returning the result, and (with one process per round) starting Python. It is a fixed cost per turn, so it matters
less the longer each site trains.

## Estimating run time
- **Round:** ≈ ⌈N ÷ K⌉ × (one site's training time at K + overhead per turn). Training gets slower as K grows (in the
  measurements, +14% at K = 4 for the Lightning model, +50% for the CNN), so measure it once at your K.
- **Job:** ≈ `num_rounds` × round time. Use it for `timeout_seconds`.
- **Example:** 8 sites, K = 4, 75 s of training at K = 4, 10 s overhead, 3 rounds: 2 waves × 85 s ≈ 170 s per round,
  ≈ 9 minutes per job.

## Monitoring
- **Server log** (FCP UI, the run's server logs): one `STAGGER {json}` line per scheduling event. Check the first
  `round_start` line: its `agents` map lists every agent with its sites and K. If each agent has only one site, the
  sites are not being grouped (see "Troubleshooting"). Each round ends with a `round_done` line and a plain
  `Round <r>: <n> of <N> sites succeeded in <s> s.`
- **`stagger_report.py`:** download the server log and run `python stagger_report.py <server-log-file>`. It prints one
  line per round and exits with 1 if an agent ever trained more than K sites at once or the job failed.
- **Site logs** (FCP UI, per workgroup): the training script's own output, including its errors.
- **GPU memory** (if you have `kubectl` access to the agent): run a small pod on the GPU node and sample `nvidia-smi`:
  ```bash
  k run gpu-mon -n <nvflare-namespace> --image=nvcr.io/nvidia/cuda:12.2.0-base-ubuntu22.04 --restart=Never -- sleep infinity
  k exec -n <nvflare-namespace> gpu-mon -- nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 > gpu.csv
  k delete pod gpu-mon -n <nvflare-namespace>
  ```

## Failures
- **A site fails** (its training process crashed or raised, it returned an error, it timed out, or it disconnected):
  the round goes on without it, and with `exclude_failed_clients` the site is skipped for the rest of the job. A site
  whose process crashed cannot rejoin the job. The server log says:
  `Site <name> failed in round <r> (<reason>); excluded from the remaining rounds; <k> sites can still succeed this round, <M> required.`
- **The job stops** as soon as a round can no longer reach `min_successful_clients`, or if fewer than `min_clients`
  sites connect before the first round:
  `Job stopped in round <r>: <n> sites succeeded, <M> required (min_successful_clients). Failed: <site: reason; ...>.`
- **Why `min_successful_clients` matters:** `min_clients` must equal the number of sites so FCP starts the job with
  all of them. If `min_successful_clients` is left at its default (`min_clients`), one failed site stops the job for
  every workgroup. Set it lower (e.g. N − 1) if a round may be aggregated without some sites.

## Troubleshooting
| Symptom | Cause and fix |
|---|---|
| Training runs on the CPU, or "no CUDA" | The image lacks `NVIDIA_VISIBLE_DEVICES` / `NVIDIA_DRIVER_CAPABILITIES` (see "Adapting your own model", step 5) |
| CUDA out of memory | K is too high for the GPU, or data was preloaded onto the GPU: lower `max_concurrent` or the batch size |
| All sites train at once; warning "staggering has no effect" | Site names don't end in `_<number>`, so every site looks like its own agent: set `agent_name_pattern` |
| A round stalls on one site | That site hung: it is dropped when `train_timeout` expires. If `train_timeout` is 0 there is no limit |
| `Site … failed …` | Read that site's log in the FCP UI for its error; the round continues without it |
| `Job stopped in round …` | Too few sites succeeded: fix the failing sites, or lower `min_successful_clients` |
| `Job stopped before training: only … sites connected` | `min_clients` is larger than the number of sites in the job, or some sites didn't start |
| The run ends with a timeout in FCP | `timeout_seconds` is too short for a staggered job (see "Timeouts") |
| Config error when the job starts | The example configs contain `//` comment lines: remove them (the example notebook does) |

## Known limits
- **A crashed site is not recovered** within the job; it is only excluded, with a clear log line.
- **No overcommit protection:** the controller doesn't check free GPU memory before starting a site.
- **The slowest site sets the round time:** a site on a slower machine (or the CPU) holds every round open.
- **Tested on one GPU type and NVFlare version only:** a single-GPU FCP agent with an NVIDIA L4, NVFlare 2.8.1. Other
  GPUs, agents with several GPUs, and other NVFlare versions have not been tested.
- **Network:** a 15-minute stall of client-server connections was seen once at 30 sites with K = 6; it was not
  reproduced and not shown to be caused by staggering.
- **Continuing a failed job:** the latest and the best global model are saved in `/output` every round, but starting a
  new job from them is not automated or tested here.

## Isolation and security
- Each site runs in its own pod and process; sites share only the GPU.
- GPU memory handed from one site to the next was checked: 15 hand-overs, 20 GB scanned each time, no data from the
  previous site. Sites training at the same time could not read each other's GPU memory.
- With one process per site, a waiting site keeps a live process (and its CUDA context) on the shared GPU between its
  turns.
- Timing and other side channels between sites that share a GPU were not assessed.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to
[support@rhinofcp.com](mailto:support@rhinofcp.com).
