# NVIDIA FLARE Example - Staggered Federated Learning with PyTorch Lightning (Chemprop) and FedAvg

## Description
This example trains a [Chemprop](https://github.com/chemprop/chemprop) model, a message-passing neural network built
on PyTorch Lightning, that predicts whether a molecule inhibits the CYP3A4 enzyme from its SMILES string. Each site
trains on its own share of the molecules, and the server averages the sites' models every round with NVFlare's
`FedAvg` workflow.

The sites share one GPU agent and **take turns** on it: at most 4 sites train at a time (configurable in
[config_fed_server.json](app/config/config_fed_server.json)), and the rest wait for a free slot. The concept, the
settings and the measured results are in the [staggered FL guide](../../README.md); this README covers what is
specific to this example and how to run it.

This is the setup most NVFlare jobs use: the `FedAvg` server workflow and the in-process client. If your job is built
on `ScatterAndGather`, use the [scatter-and-gather example](../scatter-and-gather/README.md) instead; the staggering
settings are the same.

**It shows how to:**
* Run a PyTorch Lightning model on FCP with `StaggeredFedAvg`, so many sites share one GPU
* Run the training script in-process, once per site for the whole job, which keeps optimizer and learning-rate state
  between rounds
* Let a failing site fail fast, so the job continues without it

## Requirements
- **NVFlare 2.8.1**, Chemprop 2.0.5, PyTorch Lightning 2.6.6, torch 2.14.1, Python 3.11, CUDA 12.4 base image.
- **An FCP environment with the NVFlare 2.8 code type** and **rhino_health SDK 2.1.25 or newer**
  (`CodeTypes.NVIDIA_FLARE_V2_8`).
- **A project with N collaborating workgroups whose sites run on the same GPU agent** (see "Running this example on
  FCP"). The example is set for N = 8.

## Resources
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config`
    - `config_fed_client.json` - Client config: the in-process client (`PTInProcessClientAPIExecutor`), 50 epochs per
      round. Staggering settings are commented; remove the `//` lines before using it outside the notebook
    - `config_fed_server.json` - Server config: `StaggeredFedAvg` with K = 4, sliding, 8 sites, failure handling,
      3 rounds; saves the global model to `/output/model_parameters.pt`. Commented the same way
  - `custom`
    - `__init__.py` - Empty file marking `custom` as a Python package
    - `chemprop_fl_classification.py` - The training script: loads the site's dataset, then loops over rounds
      (receive the global model, validate it, train, send back). Lines that matter for staggering are marked
      `# Staggering:`
    - `staggered_fed_avg.py` - The staggered server workflow. Copy it unchanged into your own job
- `../data/make_shards.py` - Splits the CYP3A4 data in this repository into one CSV per site (shared by the
  Chemprop examples)
- `Dockerfile` - Builds the image: CUDA 12.4 runtime, Python 3.11, the requirements, and the GPU access env vars
- `meta.json` - NVFlare job metadata, required by FCP at the container's working directory
- `notebook.ipynb` - Runs the example on FCP: makes the shards, creates the data schema and the datasets, creates the
  Code Object from your pushed image, and starts the training run
- `README.md` - This file
- `requirements.txt` - Pinned Python requirements

## How staggering is wired into this example
- **Server:** `config_fed_server.json` uses `staggered_fed_avg.StaggeredFedAvg` instead of NVFlare's `FedAvg`. Only
  how each round's training task is sent changes; FedAvg's aggregation, model saving and model selection are its own.
- **Client:** the in-process client runs the training script inside the site's client process, once for the whole
  job. Between its turns the site waits in `flare.receive()`.
- **Training script:** a normal Lightning script with `flare.patch(trainer)` and a `while flare.is_running()` loop. It
  needs no GPU cleanup: NVFlare's Lightning patch moves the model to the CPU after each round, so a waiting site holds
  only its CUDA context (~0.3 GB). The patch also restores the optimizer and LR scheduler, and the epoch count
  continues across rounds (50, 100, 150).
- **Fail fast:** the script lets errors propagate. The in-process client reports them to the server at once, so the
  site is excluded within seconds. Don't end the process yourself (`os._exit`): with the in-process client that ends
  the site's whole client process, and the server would only notice when `train_timeout` expires.
- **Image:** `NVIDIA_VISIBLE_DEVICES` and `NVIDIA_DRIVER_CAPABILITIES` give the container the GPU; FL client pods don't
  request one.

### Staggering settings
| File | Setting | Value here | Why |
|---|---|---|---|
| server | `path` | `staggered_fed_avg.StaggeredFedAvg` | The staggered workflow |
| server | `max_concurrent` | 4 | ~0.5 GB per training site, ~2 CPU cores each; 4 was 3.5× faster than 1 |
| server | `wave_mode` | `"sliding"` | A waiting site starts as soon as any slot frees |
| server | `num_clients` | 8 | **Required:** the number of sites. The notebook sets it from your datasets |
| server | `min_successful_clients` | 7 | One failed site doesn't stop the job for everyone |
| server | `exclude_failed_clients` | `true` | A failed site is skipped in later rounds |
| server | `max_retries` | 0 | A site whose training failed usually fails again |
| server | `train_timeout` | 900 | One site trains for ~75 s here; 900 s leaves room for larger data |
| server | `agent_max_concurrent`, `agent_name_pattern`, `wait_for_clients_timeout` | defaults | See the guide |
| client | `path` | `PTInProcessClientAPIExecutor` | The script runs once per site for the whole job, inside the site's client process; state kept between rounds. The other option is `PTClientAPILauncherExecutor` with a `SubprocessLauncher` (`launch_once: true`), which runs the script as its own process (see the [scatter-and-gather example](../scatter-and-gather/README.md) and "Choosing the client mode" in the guide) |
| client | `task_script_args` | `--epochs-per-round 50` | Local epochs per round |

**`num_clients`, not `min_clients`:** `FedAvg` has no `min_clients` argument. `StaggeredFedAvg` reads `num_clients` as
the number of sites in the job and trains every site every round (FedAvg's sampling is not used). FCP reads
`min_clients` to decide when to start a job; with none set, it waits for every site the run asked for, which is what
staggering needs.

Script flags (set through `task_script_args`): `--epochs-per-round` (default 50), `--batch-size` (64),
`--num-workers` (0).

## Running this example on FCP
1. **Workgroups and agent.** You need a project with N workgroups collaborating in it, and every workgroup's site must
   run on the same GPU agent. Rhino support sets this up on request: putting several workgroups on one agent needs a
   Rhino admin. Give the site workgroups a common name prefix (e.g. `stagger-site-01` … `stagger-site-08`); the
   notebook finds them by it.
2. **Build and push the image** to your workgroup's container registry (see
   [Pushing Containers to the ECR](https://docs.rhinofcp.com/getting-started/quick-start-guide/pushing-containers-to-the-ecr)):
   ```bash
   # cd examples/nvflare/staggered-fl/lightning-chemprop/fedavg
   ../../../../../utils/docker-push.sh <your-workgroup-repo-name> <a-tag-you-choose>
   ```
   It prints `Container image URI: ...` when done; copy that URI into the notebook.
3. **Run `notebook.ipynb`**. Its first cell installs `rhino_health` and `pandas`; set `RHINO_API_URL` to your FCP
   environment. It:
   - finds your project and its site workgroups by name prefix;
   - splits the CYP3A4 data into one file per site (`../data/shards/shard_01.csv` …, about 1,375 molecules each, with
     the columns `id`, `smiles` and `cyp3a4`). **You copy `../data/shards` to the GPU agent's storage**, or to a
     bucket connected to it as Client Mounted Storage, when the notebook asks: it can't reach the agent's disk;
   - creates the data schema for the shards;
   - registers one shard as a dataset in each site workgroup. This needs you to be a member of every site workgroup;
     if you aren't, register them in the FCP UI (**Datasets → Add Dataset**, once per workgroup) and set
     `REGISTER_DATASETS = False`;
   - creates the Code Object (`CodeTypes.NVIDIA_FLARE_V2_8`) from your image;
   - reads the two configs, removes the `//` comment lines, and sets `num_clients` to the number of datasets;
   - computes `timeout_seconds` from the number of sites, K and the rounds;
   - starts the training run, waits for it, and runs `../../stagger_report.py` on its server log (the FCP UI can't
     download logs, so the notebook saves the log with the SDK);
   - downloads the trained model.
4. **Check the run.** In the run's server log, the first `STAGGER` `round_start` line should list one agent with all
   N sites and `max_concurrent` 4, and each round should end with `Round <r>: 8 of 8 sites succeeded`. The notebook's
   "Check the staggering" cell checks that no more than 4 sites trained at once.

Expected results (8 sites, one NVIDIA L4 GPU): rounds of about 2.7 minutes, peak GPU memory about 3.2 GB, and a
global validation ROC AUC of about 0.84 after 3 rounds.

## Cleanup
- `rm -rf ../data/shards` removes the local shard files.
- The notebook's last cell removes the Code Object it created when `CLEANUP = True`. It doesn't touch your
  project, workgroups, data schema or datasets, the shards on the agent, or the pushed image.

## Using your own model
Follow "Adapting your own model" in the [staggered FL guide](../../README.md). In this example, the parts to copy are
`staggered_fed_avg.py`, the lines marked `# Staggering:` in the script, the commented settings in both configs, and
the two `NVIDIA_*` lines in the `Dockerfile`.

## Data
The molecules come from `examples/site-testing-life-science/data/cyp3a4_all_no_test.csv`, which this repository
already ships for its site-testing examples: SMILES strings of small molecules labelled as CYP3A4 inhibitors or not.
No patient data is involved, and `make_shards.py` adds no new data, it only splits that file.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to
[support@rhinofcp.com](mailto:support@rhinofcp.com).
