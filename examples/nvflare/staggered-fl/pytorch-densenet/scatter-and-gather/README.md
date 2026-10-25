# NVIDIA FLARE Example - Staggered Federated Learning with PyTorch (DenseNet-121)

## Description
This example trains a DenseNet-121 image classifier, written in plain PyTorch, that predicts whether a chest X-ray
shows pneumonia. It starts from the ImageNet weights. Each site trains on its own patients' images, and the server
averages the sites' models every round with NVFlare's `ScatterAndGather` workflow.

The sites share one GPU agent and **take turns** on it: at most 4 sites train at a time (configurable in
[config_fed_server.json](app/config/config_fed_server.json)), and the rest wait for a free slot. The concept, the
settings and the measured results are in the [staggered FL guide](../../README.md); this README covers what is
specific to this example and how to run it.

This is the example to start from when your training script is plain PyTorch (your own training loop, no Lightning).
A plain-PyTorch script has to free its GPU memory between turns itself; this example shows how.

**It shows how to:**
* Run a plain PyTorch model on FCP with `StaggeredScatterAndGather`, so many sites share one GPU
* Run the training script in-process, once per site for the whole job, and free the model after each round so a
  waiting site holds only ~0.3 GB of GPU memory
* Let a failing site fail fast, so the job continues without it

## Requirements
- **NVFlare 2.8.1**, torch 2.11.0, torchvision 0.26.0, Python 3.12, CUDA 13.0 base image.
- **An FCP environment with the NVFlare 2.8 code type** and **rhino_health SDK 2.1.25 or newer**
  (`CodeTypes.NVIDIA_FLARE_V2_8`).
- **A project with N collaborating workgroups whose sites run on the same GPU agent** (see "Running this example on
  FCP"). The example is set for N = 8.
- **The Kaggle "Chest X-Ray Images (Pneumonia)" archive** (`archive.zip`, ~2.3 GB), downloaded from Kaggle (see
  "Data"). No need to unzip it.

## Resources
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config`
    - `config_fed_client.json` - Client config: the in-process client (`PTInProcessClientAPIExecutor`), 200 training
      steps per round. Staggering settings are commented; remove the `//` lines before using it outside the notebook
    - `config_fed_server.json` - Server config: `StaggeredScatterAndGather` with K = 4, sliding, 8 sites, failure
      handling, 3 rounds; saves the global model to `/output/model_parameters.pt` and keeps the best one by
      validation ROC AUC. Commented the same way
  - `custom`
    - `__init__.py` - Empty file marking `custom` as a Python package
    - `densenet_pneumonia_training.py` - The training script: loads the site's images, then loops over rounds
      (receive the global model, validate it, train, free the GPU, send back). Lines that matter for staggering are
      marked `# Staggering:`
    - `network.py` - The model: DenseNet-121 with a two-class head
    - `staggered_scatter_and_gather.py` - The staggered server workflow.
- `../data/make_shards.py` - Takes about 150 images per site from the Kaggle archive and splits them into one dataset
  per site, by patient
- `Dockerfile` - Builds the image: CUDA 13.0 runtime, Python 3.12, the requirements, the DenseNet-121 ImageNet weights,
  and the GPU access env vars
- `meta.json` - NVFlare job metadata, required by FCP at the container's working directory
- `notebook.ipynb` - Runs the example on FCP: makes the shards, creates the data schema and the datasets, creates the
  Code Object from your pushed image, and starts the training run
- `README.md` - This file
- `requirements.txt` - Pinned Python requirements

## How staggering is wired into this example
- **Server:** `config_fed_server.json` uses `staggered_scatter_and_gather.StaggeredScatterAndGather` instead of
  `ScatterAndGather`. Everything else (aggregator, persistor, model selector) is a regular NVFlare job.
- **Client:** the in-process client runs the training script inside the site's client process, once for the whole
  job. Between its turns the site waits in `flare.receive()`.
- **Training script:** a regular NVFlare Client API script with a `while flare.is_running()` loop. Because the script
  keeps running between its turns, it **frees the GPU at the end of every round**: it copies the weights to the CPU
  for `flare.send`, deletes the model, and empties PyTorch's cache. A waiting site then holds only its CUDA context
  (~0.3 GB) instead of its training footprint (~2.7 GB). Without this, every waiting site would keep its full
  footprint and K = 4 with 8 sites would no longer fit the way it does here.
- **Fail fast:** the script lets errors propagate. The in-process client reports them to the server at once, so the
  site is excluded within seconds. Don't end the process yourself (`os._exit`): with the in-process client that ends
  the site's whole client process, and the server would only notice when `train_timeout` expires.
- **Image:** `NVIDIA_VISIBLE_DEVICES` and `NVIDIA_DRIVER_CAPABILITIES` give the container the GPU; FL client pods don't
  request one.

### Staggering settings
| File | Setting | Value here | Why |
|---|---|---|---|
| server | `path` | `staggered_scatter_and_gather.StaggeredScatterAndGather` | The staggered workflow |
| server | `max_concurrent` | 4 | ~2.7 GB per training site, ~0.3 GB per waiting site: 4 × 2.7 + 4 × 0.3 ≈ 12 GB on a 23 GB GPU. 4 was 2.9× faster than 1; 6 was no faster |
| server | `wave_mode` | `"sliding"` | A waiting site starts as soon as any slot frees |
| server | `min_clients` | 8 | **Required:** the number of sites. The notebook sets it from your datasets |
| server | `min_successful_clients` | 7 | One failed site doesn't stop the job for everyone |
| server | `exclude_failed_clients` | `true` | A failed site is skipped in later rounds |
| server | `max_retries` | 0 | A site whose training failed usually fails again |
| server | `train_timeout` | 900 | One site trains for ~90 s here; 900 s leaves room for larger data |
| server | `agent_max_concurrent`, `agent_name_pattern`, `wait_for_clients_timeout` | defaults | See the guide |
| client | `path` | `PTInProcessClientAPIExecutor` | The script runs once per site for the whole job, inside the site's client process. The other option is `PTClientAPILauncherExecutor` with a `SubprocessLauncher` (`launch_once: true`), which runs the script as its own process (see the [Lightning scatter-and-gather example](../../lightning-chemprop/scatter-and-gather/README.md) and "Choosing the client mode" in the guide) |
| client | `task_script_args` | `--local-steps 200` | Training steps (batches of 32) per round |

Script flags (set through `task_script_args`): `--local-steps` (default 200), `--batch-size` (32), `--lr` (1e-4),
`--image-size` (224), `--num-workers` (4), `--no-amp` (train in full precision).

The script creates a new optimizer every round, so Adam's state is not carried between rounds. To keep it, move the
optimizer state to the CPU before freeing the model and back to the GPU on the next turn.

## Running this example on FCP
1. **Workgroups and agent.** You need a project with N workgroups collaborating in it, and every workgroup's site must
   run on the same GPU agent. Rhino support sets this up on request: putting several workgroups on one agent needs a
   Rhino admin. Give the site workgroups a common name prefix (e.g. `stagger-site-01` … `stagger-site-08`); the
   notebook finds them by it.
2. **Download the data.** Download the archive from
   [Kaggle](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) to `../data/archive.zip`, or
   anywhere and set `ARCHIVE` in the notebook. There is no need to unzip it (see "Data").
3. **Build and push the image** to your workgroup's container registry (see
   [Pushing Containers to the ECR](https://docs.rhinofcp.com/getting-started/quick-start-guide/pushing-containers-to-the-ecr)):
   ```bash
   # cd examples/nvflare/staggered-fl/pytorch-densenet/scatter-and-gather
   ../../../../../utils/docker-push.sh <your-workgroup-repo-name> <a-tag-you-choose>
   ```
   It prints `Container image URI: ...` when done; copy that URI into the notebook.
4. **Run `notebook.ipynb`**. Its first cell installs `rhino_health` and `pandas`; set `RHINO_API_URL` to your FCP
   environment. It:
   - finds your project and its site workgroups by name prefix;
   - takes about 150 images per site from the archive and splits them by patient: `../data/images/` (the images,
     flat, under unique names) and `../data/shards/shard_01.csv` … (one per site, with the columns `JPG_file`,
     `Patient_ID` and `Pneumonia`);
   - **you then copy `../data/images` and `../data/shards`, side by side in one folder, to the GPU agent's storage** or
     to a bucket connected to it as Client Mounted Storage, and set `DATA_LOCATION` to that folder as the agent sees
     it (the notebook can't reach the agent's disk):
     ```
     <DATA_LOCATION>/
     ├── images/   all the .jpeg files, flat
     └── shards/   shard_01.csv … shard_NN.csv
     ```
   - creates the data schema for the shards (`JPG_file` is a file name, so the import copies each image into the
     site's dataset);
   - registers one shard as a dataset in each site workgroup. This needs you to be a member of every site workgroup;
     if you aren't, register them in the FCP UI (**Datasets → Add Dataset**, once per workgroup) and set
     `REGISTER_DATASETS = False`;
   - creates the Code Object (`CodeTypes.NVIDIA_FLARE_V2_8`) from your image;
   - reads the two configs, removes the `//` comment lines, and sets `min_clients` to the number of datasets;
   - computes `timeout_seconds` from the number of sites, K and the rounds;
   - starts the training run, waits for it, and runs `../../stagger_report.py` on its server log (the FCP UI can't
     download logs, so the notebook saves the log with the SDK);
   - downloads the trained model.
5. **Check the run.** In the run's server log, the first `STAGGER` `round_start` line should list one agent with all
   N sites and `max_concurrent` 4, and each round should end with `Round <r>: 8 of 8 sites succeeded`. The notebook's
   "Check the staggering" cell checks that no more than 4 sites trained at once.

Expected results (8 sites, ~150 images each, one NVIDIA L4 GPU): rounds of about 3.5 minutes (one site trains for
about 90 s), peak GPU memory about 12 GB, about 0.3 GB per waiting site, and a validation ROC AUC of about 0.99 after
the first round.

## Cleanup
- `rm -rf ../data/images ../data/shards` removes the local images and shard files.
- The notebook's last cell removes the Code Object it created when `CLEANUP = True`. It doesn't touch your
  project, workgroups, data schema or datasets, the data on the agent, or the pushed image.

## Using your own model
Follow "Adapting your own model" in the [staggered FL guide](../../README.md). In this example, the parts to copy are
`staggered_scatter_and_gather.py`, the lines marked `# Staggering:` in the script (the round loop and the GPU cleanup
at the end of each round), the commented settings in both configs, and the two `NVIDIA_*` lines in the `Dockerfile`.

## Data
For this example, we used the
[Kaggle Chest X-Ray Images (Pneumonia) dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia):
5,856 chest X-rays (JPEG) labelled normal or pneumonia, to simulate sites that each hold their own patients' images.

The data is not in this repository. Download the archive from Kaggle (see above) and run `make_shards.py` on the zip
(the notebook does this for you). It takes about 150 images per site, which is enough to show the staggering;
`--images-per-site 0` uses all 5,856 images, and the time per round stays the same because each round trains a fixed
number of steps. Patients are read from the file names, and all images of one patient go to the same site.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to
[support@rhinofcp.com](mailto:support@rhinofcp.com).
