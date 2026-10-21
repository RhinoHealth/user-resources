# NVIDIA FLARE Example - Staggered Federated Learning with PyTorch Lightning (Chemprop)
> Last validated: pending (validation on FCP is in progress)

## Description
This example trains a [Chemprop](https://github.com/chemprop/chemprop) model, a message-passing neural network built
on PyTorch Lightning, that predicts whether a molecule inhibits the CYP3A4 enzyme from its SMILES string. Each site
trains on its own share of the molecules, and the server averages the sites' models every round.

The sites share one GPU agent and **take turns** on it: at most 4 sites train at a time (configurable in [config_fed_server.json](app/config/config_fed_server.json)), and the rest wait for a free
slot. The concept, the settings and the measured results are in the [staggered FL guide](../../README.md); this README
covers what is specific to this example and how to run it.

**It shows how to:**
* Run a PyTorch Lightning model on FCP with `StaggeredScatterAndGather`, so many sites share one GPU
* Keep one training process per site for the whole job, which keeps optimizer and learning-rate state between rounds
* Make a failing site fail fast, so the job continues without it

## Requirements
- **NVFlare 2.8.1**, Chemprop 2.0.5, PyTorch Lightning 2.6.6, torch 2.14.1, Python 3.11, CUDA 12.4 base image.
- **An FCP environment with the NVFlare 2.8 code type**, and for the notebook **rhino_health SDK 2.1.25 or newer**
  (`CodeTypes.NVIDIA_FLARE_V2_8`).
- **A project with N collaborating workgroups whose sites run on the same GPU agent** (see "Running this example on
  FCP"). The example is set for N = 8.

## Resources
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config`
    - `config_fed_client.json` - Client config: one training process per site (`launch_once: true`), 50 epochs per
      round, timeouts. Staggering settings are commented; remove the `//` lines before using it (step 6 below)
    - `config_fed_server.json` - Server config: `StaggeredScatterAndGather` with K = 4, sliding, 8 sites, failure
      handling, 3 rounds; saves the global model to `/output/model_parameters.pt`. Commented the same way
  - `custom`
    - `__init__.py` - Empty file marking `custom` as a Python package
    - `chemprop_fl_classification.py` - The training script: loads the site's dataset, then loops over rounds
      (receive the global model, validate it, train, send back). Lines that matter for staggering are marked
      `# Staggering:`
    - `staggered_scatter_and_gather.py` - The staggered server workflow. Copy it unchanged into your own job
- `../data/make_shards.py` - Splits the CYP3A4 data in this repository into one CSV per site (shared by the
  Chemprop examples)
- `Dockerfile` - Builds the image: CUDA 12.4 runtime, Python 3.11, the requirements, and the GPU access env vars
- `meta.json` - NVFlare job metadata, required by FCP at the container's working directory
- `notebook.ipynb` - Runs steps 3 to 8 of "Running this example on FCP" with the SDK: makes the shards, creates the
  data schema and the datasets, creates the Code Object from your pushed image, starts the training run, checks the
  staggering and downloads the model
- `README.md` - This file
- `requirements.txt` - Pinned Python requirements

## How staggering is wired into this example
- **Server:** `config_fed_server.json` uses `staggered_scatter_and_gather.StaggeredScatterAndGather` instead of
  `ScatterAndGather`. Everything else (aggregator, persistor, model selector) is a regular NVFlare job.
- **Client:** `"launch_once": true` starts one training process per site for the whole job. Between its turns the site
  waits in `flare.receive()`.
- **Training script:** a normal Lightning script with `flare.patch(trainer)` and a `while flare.is_running()` loop. It
  needs no GPU cleanup: NVFlare's Lightning patch moves the model to the CPU after each round, so a waiting site holds
  only its CUDA context (~0.3 GB). The patch also restores the optimizer and LR scheduler, and the epoch count
  continues across rounds (50, 100, 150).
- **Fail fast:** the script's entry point ends the process on any error, so the server excludes the site within
  seconds instead of after `heartbeat_timeout` (10 minutes).
- **Image:** `NVIDIA_VISIBLE_DEVICES` and `NVIDIA_DRIVER_CAPABILITIES` give the container the GPU; FL client pods don't
  request one.

### Staggering settings
| File | Setting | Value here | Why                                                                     |
|---|---|---|-------------------------------------------------------------------------|
| server | `path` | `staggered_scatter_and_gather.StaggeredScatterAndGather` | The staggered workflow                                                  |
| server | `max_concurrent` | 4 | ~0.5 GB per training site, ~2 CPU cores each; 4 was 3.5× faster than 1  |
| server | `wave_mode` | `"sliding"` | A waiting site starts as soon as any slot frees                         |
| server | `min_clients` | 8 | **Required:** the number of sites                                        |
| server | `min_successful_clients` | 7 | One failed site doesn't stop the job for everyone                       |
| server | `exclude_failed_clients` | `true` | A failed site is skipped in later rounds                                |
| server | `max_retries` | 0 | A crashed site doesn't come back                                        |
| server | `train_timeout` | 900 | One site trains for ~75 s here; 900 s leaves room for larger data       |
| server | `agent_max_concurrent`, `agent_name_pattern`, `wait_for_clients_timeout` | defaults | See the guide                                                           |
| client | `launch_once` | `true` | One process per site: ~10% faster, state kept between rounds            |
| client | `app_config` | `--epochs-per-round 50` | Local epochs per round                                                  |
| client | `external_pre_init_timeout`, `heartbeat_timeout` | 600 | Room for slow start-up and long training steps                          |

Script flags (set through `app_config`): `--epochs-per-round` (default 50), `--batch-size` (64), `--num-workers` (0).

## Running this example on FCP
1. **Workgroups and agent.** You need a project with N workgroups collaborating in it, and every workgroup's site must
   run on the same GPU agent. Rhino support sets this up on request: putting several workgroups on one agent needs a
   Rhino admin. Give the site workgroups a common name prefix (e.g. `stagger-site-01` …
   `stagger-site-08`); the notebook finds them by it.
2. **Build and push the image** to your workgroup's container registry (see
   [Pushing Containers to the ECR](https://docs.rhinofcp.com/getting-started/quick-start-guide/pushing-containers-to-the-ecr)):
   ```bash
   # cd examples/nvflare/staggered-fl/lightning-chemprop/scatter-and-gather
   ../../../../../utils/docker-push.sh <your-workgroup-repo-name> <a-tag-you-choose>
   ```
   It prints `Container image URI: ...` when done; you need that URI in step 5.

   **Steps 3 to 8 can run from `notebook.ipynb`** instead of by hand. It needs you to be a member of every site
   workgroup, and the shard files on the agent (step 4) before it registers the datasets.
3. **Make the data shards**, one CSV per site (needs `pip install pandas`):
   ```bash
   python ../data/make_shards.py --num-shards <N>
   ```
   This writes `../data/shards/shard_01.csv` … `shard_NN.csv`, with the columns `id`, `smiles` and `cyp3a4` (about
   1,375 molecules each for N = 8).
4. **Upload the datasets**, one shard to each site workgroup. Put the shard files where the GPU agent can read them:
   its storage, or a bucket connected to it as Client Mounted Storage (paths under `/rhino_data/external/...`). Then,
   in the FCP UI, switch to each site workgroup in turn and add its shard under **Datasets → Add Dataset**: shard 1 in
   the first workgroup, shard 2 in the second, and so on. Use the same data schema for all of them, with `id` and
   `smiles` as String inputs and `cyp3a4` as an Integer output. Wait until every dataset has finished importing.
5. **Create the Code Object** in the project: type **NVIDIA FLARE v2.8**, the shards' data schema as its input, and
   the container image URI from step 2.
6. **Run the training** from the Code Object (**Run Model Training**):
   - select the N datasets;
   - **Timeout in seconds**: `num_rounds × ⌈N ÷ 4⌉ × 85 × 1.3`, and at least 1800 (1800 for N = 8);
   - **Federated server config override** and **Federated client config override**: paste
     `config_fed_server.json` and `config_fed_client.json` without their `//` comment lines, which the image's copies
     still have. This prints them without the comments:
     ```bash
     grep -v '^[[:space:]]*//' app/config/config_fed_server.json
     grep -v '^[[:space:]]*//' app/config/config_fed_client.json
     ```
     If N isn't 8, set `min_clients` in the server config to N, and `min_successful_clients` to at most N.
7. **Check the run.** In the run's server log, the first `STAGGER` `round_start` line should list one agent with all
   N sites and `max_concurrent` 4, and each round should end with `Round <r>: N of N sites succeeded`. To check that
   no more than 4 sites trained at once, save the server log to a file and run
   `python ../../stagger_report.py <server-log-file>`. The FCP UI can't download logs: copy the server log from the
   run's logs, or save it with the SDK as the notebook's "Check the staggering" cell does.
8. **Download the trained model** from **Code Runs**: the 3 dots next to the run, **Download Model Parameters**.

Expected results (8 sites, one NVIDIA L4 GPU): rounds of about 3 minutes, peak GPU memory about 3.2 GB, and a
global validation ROC AUC of about 0.84 after 3 rounds.

## Cleanup
- `rm -rf ../data/shards` removes the local shard files.
- Remove the Code Object, the datasets and the uploaded shard files in FCP when you no longer need them. The
  notebook's last cell removes the Code Object it created when `CLEANUP = True`.

## Using your own model
Follow "Adapting your own model" in the [staggered FL guide](../../README.md). In this example, the parts to copy are
`staggered_scatter_and_gather.py`, the lines marked `# Staggering:` in the script, the commented settings in both
configs, and the two `NVIDIA_*` lines in the `Dockerfile`.

## Data
The molecules come from `examples/site-testing-life-science/data/cyp3a4_all_no_test.csv`, which this repository
already ships for its site-testing examples: SMILES strings of small molecules labelled as CYP3A4 inhibitors or not.
No patient data is involved, and `make_shards.py` adds no new data, it only splits that file.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to
[support@rhinofcp.com](mailto:support@rhinofcp.com).
