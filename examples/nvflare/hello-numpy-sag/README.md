# NVIDIA FLARE Example - Hello Numpy Scatter and Gather
> Last validated: 2026-09-15

## Description
This example adapts NVIDIA's [Hello Numpy Scatter and Gather](https://nvflare.readthedocs.io/en/2.4/examples/hello_scatter_and_gather.html) NVIDIA FLARE example to run on Rhino's Federated Computing Platform (FCP). 

The "model" is just a 3x3 array that gets incremented by 1 each round, so there's no real training or dataset to worry about; the point is to see the full federated plumbing (client, server, rounds) work end to end.

**It shows how to:**
* Use model code adapted to NVIDIA FLARE (NVFlare), and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

## Requirements
This example uses **NVFlare 2.6.0** & **Python 3.12**.

**NVFlare must stay at 2.6.0 for this example**: FCP's server-side provisioning only has templates for NVFlare versions up to and including 2.6 - there's no newer option available on the platform at all. A container pinned to a newer NVFlare (e.g. 2.7+/2.8.x) will fail on FCP with confusing, indirect errors - a client error like `missing 'target' in server config ... the startup kit may have been provisioned with an older HA-based template`, or a server error like `Can't load class nvflare.app_common.logging.log_receiver.LogReceiver` - both symptoms of FCP generating a v2.6-era startup kit for a newer NVFlare that no longer matches it. This is unrelated to the local Docker walkthrough below, which has no provisioning-template dependency and can safely use a newer NVFlare - see "Using a different Python or NVFlare version" at the bottom.

## Resources
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config` - This is the standard NVFlare directory for config files
  - `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA examples, but with the inputs being read from the `/input` folder in order to work with FCP
- `data` - A folder with some example data (`dataset.csv`) to train/test with locally, before deploying to FCP
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `infer.py` - A script for running inference on the trained model. The model in this example is a simple placeholder, so `infer.py` likewise emits a placeholder `SCORE` column rather than a real prediction - swap in your own model and scoring logic for real use cases.
- `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`) - required by FCP's provisioning for NVFlare >= 2.4; FCP reads this straight from the running container, so it must exist at the container's WORKDIR
- `model_parameters.npy` - Example output, which is produced from running this demo
- `notebook.ipynb` - A runnable notebook for the "Running this example on FCP" walkthrough below - authenticates, registers a dataset, creates the Code Object, trains, and downloads the trained weights
- `README.md` - This file
- `requirements.txt` - The python requirements for this project

## Running this example locally
The trained model and inference output are written to `/output`, matching how FCP mounts your container. Run this example inside Docker so `/input` and `/output` behave the same way they will on FCP.

1. **(Optional) Create a virtual environment and install dependencies**, to confirm `requirements.txt` resolves cleanly on your machine before building the image:
   ```bash
   python -m venv venv
   source venv/bin/activate

   # make sure you run this from within the hello-numpy-sag repo
   pip install -r requirements.txt
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t hello-numpy-sag .
   ```

3. **Set up local input/output folders and start a container shell**, with `/input` and `/output` mounted in:
   ```bash
   mkdir -p ~/nvflare-test/input ~/nvflare-test/output
   cp data/dataset.csv ~/nvflare-test/input/dataset.csv

   docker run -it --rm \
     -v ~/nvflare-test/input:/input \
     -v ~/nvflare-test/output:/output \
     hello-numpy-sag bash
   ```
   (`--rm` deletes the container automatically when you exit it, so it doesn't linger around and block `docker rmi hello-numpy-sag` later during cleanup.)

4. **Inside the container, run the FL Simulator** (1 client, 1 thread is enough for this example):
   ```bash
   nvflare simulator -w /tmp/nvflare-workspace -n 1 -t 1 .
   ```
   You should see log output for 3 rounds of Scatter-and-Gather training, ending with `Finished ScatterAndGather Training.` This step produces the trained model file, `/output/model_parameters.npy` - training and saving that file is all this step does; nothing has been scored or tested against it yet.

5. **Test inference** against the trained model, still inside the container. This is a separate step from training above - it takes the model file training just produced and actually uses it to score some data:
   ```bash
   python infer.py /output/model_parameters.npy
   cat /output/dataset.csv   # should show a SCORE column added
   ```
   Note that the `SCORE` column will always be `1`, for every row - `infer.py` hardcodes `scores = [1 for row in rows]` rather than doing any real scoring, since (as noted above) there's no real model here to make predictions with. This is expected, not a bug - swap in real scoring logic once you're adapting this example for an actual use case.

6. `exit` the container when done. Since `/input` and `/output` were mounted from your machine, the output is also visible on your host at `~/nvflare-test/output`.

## Running this example on FCP
`notebook.ipynb` walks through the whole FCP flow end-to-end: it authenticates, creates a project, registers a (trivial, unused-by-training) dataset, creates the Code Object from your pushed image, trains, and downloads the resulting weights. It needs `rhino_health` installed (`pip install rhino_health`).

**Downloading the weights is not the same as running inference.** The notebook's download step just fetches the trained `model_parameters.npy` file from FCP onto your computer - a plain file transfer, nothing computed. This example doesn't run inference on FCP at all; to actually score anything with the downloaded model, run `infer.py` locally, inside the `hello-numpy-sag` Docker container, the same way as step 5 of "Running this example locally" above (swap in the downloaded file in place of the one produced by local training).

## Cleanup
**Locally:**
- Remove the local Docker image, if you built one: `docker rmi hello-numpy-sag`
- Remove the local test scratch directory: `rm -rf ~/nvflare-test`

**On FCP:** `notebook.ipynb` creates a new Project (with a Dataset and Code Object inside it) every time it runs. Its last cell is guarded behind a `CLEANUP = False` flag - set it to `True` and re-run that cell to remove them via the SDK once you're done. This does not delete the pushed container image from your registry.

## Using a different Python or NVFlare version
**This only applies to the local Docker walkthrough** - the "Running this example on FCP" flow must stay on NVFlare 2.6.0 regardless of Python version, per the constraint under "Requirements" above.
- If your local environment needs to stay on **Python 3.8**, use **NVFlare 2.4.2**, and keep `python:3.8-slim-bullseye` as the `Dockerfile` base image.
- For any other Python/NVFlare pairing, update the `nvflare==` line in `requirements.txt` and the base image in the `Dockerfile` accordingly, then re-run the local steps above to confirm training and inference both complete successfully.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).