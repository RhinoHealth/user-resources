# NVIDIA FLARE Example - Hello PyTorch
> Last validated: 2026-09-16

## **Description**

This example adapts NVIDIA's [Hello PyTorch](https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-pt) NVIDIA FLARE example to run on Rhino's Federated Computing Platform (FCP).

**It shows how to:**
* Use PyTorch model code adapted to NVIDIA FLARE (NVFlare), and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

Please see [RhinoDocs](docs.rhinofcp.com) for more info on RhinoFCP.

## **Requirements**

This example uses **NVFlare 2.6.0**, **torch 2.4.0**, and **torchvision 0.19.0** on **Python 3.12**.

**NVFlare must stay at 2.6.0 for this example**: FCP's server-side provisioning only has templates for NVFlare versions up to and including 2.6 - there's no newer option available on the platform at all. A container pinned to a newer NVFlare (e.g. 2.7+/2.8.x) will fail on FCP with confusing, indirect errors - a client error like `missing 'target' in server config ... the startup kit may have been provisioned with an older HA-based template`, or a server error like `Can't load class nvflare.app_common.logging.log_receiver.LogReceiver` - both symptoms of FCP generating a v2.6-era startup kit for a newer NVFlare that no longer matches it. This is unrelated to the local Docker walkthrough below, which has no provisioning-template dependency and can safely use a newer NVFlare - see "Using a different Python or NVFlare version" at the bottom.

## **Resources**
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config` - This is the standard NVFlare directory for config files
    - `config_fed_client.json` - The standard NVFlare federated client config, setting to 4 epochs for the example
    - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
  - `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA examples, but with the inputs being read from the `/input` folder in order to work with FCP
    - `__init__.py` - Empty file marking `custom` as a Python package, so its modules can import from each other
    - `cifar10trainer.py` - The federated client-side training code: loads a small CIFAR-10-style image dataset from `/input/datasets/<dataset_uid>/file_data/train` (see "Running this example on FCP" below for what that path means), trains `SimpleNetwork` locally for a few epochs each round, and sends the updated weights back to the server
    - `pt_constants.py` - Shared filename/path constants used by the trainer when saving/loading its local model checkpoint between rounds
    - `simple_network.py` - The PyTorch model architecture itself - a small CNN for 10-class image classification
- `data` - Example data to train/test with, not used directly by the Docker image (only referenced by the walkthroughs below)
  - `train_data.zip` - Zipped training images, one folder per class (`0`-`9`) once extracted - used by both the local walkthrough (step 2) and `notebook.ipynb`'s FCP walkthrough
  - `test_data.zip` - Zipped test images (same per-class structure) plus labels, used for the local inference walkthrough (step 4) and testing an FCP-trained model locally afterward
  - `input_schema.csv` / `output_schema.csv` - Rhino FCP data schema definitions describing this example's input/output columns (`image_name`, `category`, `prediction`) - reference material, not consumed directly by any script here
  - `test/data_test.csv` - A small standalone sample of test rows, separate from what's inside `test_data.zip`
  - `train/cohorts/0/data_train.csv` - A cohort-style manifest of the training images (referencing the same files as `train_data.zip`) - not currently used by `notebook.ipynb`'s dataset registration, which registers `train/` directly instead; kept here for reference
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `infer.py` - A script for running inference on the trained model: loads `SimpleNetwork` with the trained weights, reads test images from `/input/file_data` and their labels from `/input/dataset.csv`, scores each image, and writes the result back to `/output/dataset.csv` with an added `Model_Score` column
- `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`) - required by FCP's provisioning for NVFlare >= 2.4; FCP reads this straight from the running container, so it must exist at the container's WORKDIR
- `notebook.ipynb` - A runnable notebook for the "Running this example on FCP" walkthrough below - authenticates, registers a dataset, creates the Code Object, trains, and downloads the resulting weights
- `README.md` - This file
- `requirements.txt` - The python requirements for this project

## **Running this example locally**

The trained model and inference output are written to `/output`, matching how FCP mounts your container. Run this example inside Docker so `/input` and `/output` behave the same way they will on FCP.

1. **Build the Docker image:**
   ```bash
   # cd examples/nvflare/hello-pt-rhino
   docker build -t hello-pt .
   ```

2. **Prepare the training data mount.** `cifar10trainer.py` reads training data from `/input/datasets/<dataset_uid>/file_data`, matching the real per-dataset layout FCP's on-prem agent mounts for NVFlare training (unlike `infer.py`'s flat `/input/file_data`, which matches a different, single-dataset execution path) - so mount a fake dataset UID folder locally too:
   ```bash
   mkdir -p ~/hellopt-test/train_mount/datasets/local-dataset/file_data
   cd ~/hellopt-test/train_mount/datasets/local-dataset/file_data

   # update this path to the location of your training data
   unzip <UPDATE_YOUR_PATH>/user-resources/examples/nvflare/hello-pt-rhino/data/train_data.zip 

   # creates file_data/train/0 ... file_data/train/9
   mkdir -p ~/hellopt-test/output
   ```

3. **Run training**, with `/input` and `/output` mounted in:
   ```bash
   docker run -it --rm \
     -v ~/hellopt-test/train_mount:/input \
     -v ~/hellopt-test/output:/output \
     hello-pt bash
   ```
   (`--rm` deletes the container automatically when you exit it, so it doesn't linger around and block `docker rmi hello-pt` later during cleanup.)
   Inside the container:
   ```bash
   nvflare simulator -w /tmp/nvflare-workspace -n 1 -t 1 .
   ```
   You should see log output for 2 rounds of Scatter-and-Gather training, ending with `Finished ScatterAndGather Training.` This step produces the trained model file, `/output/model_parameters.pt` - training and saving that file is all this step does; nothing has been scored or tested against it yet. Confirm the model was saved:
   ```bash
   ls -la /output   # should show model_parameters.pt
   ```
   `exit` the container when done.

4. **Prepare the inference data mount** (separate from training - classes go directly under `file_data`, with no `train`/`test` prefix folder):
   ```bash
   mkdir -p ~/hellopt-test/infer_mount/file_data
   cd /tmp

   # update this path to the location of your test data
   unzip <UPDATE_YOUR_PATH>/user-resources/examples/nvflare/hello-pt-rhino/data/test_data.zip -d test_extract
   
   for d in test_extract/test/*/; do
     cls=$(basename "$d")
     mkdir -p ~/hellopt-test/infer_mount/file_data/$cls
     cp "$d"*.png ~/hellopt-test/infer_mount/file_data/$cls/
   done
   cp /tmp/test_extract/test/cohort_data_test.csv ~/hellopt-test/infer_mount/dataset.csv
   ```

5. **Run inference** against the trained model. This is a separate step from training above - it takes the model file training just produced and actually uses it to score some data:
   ```bash
   docker run -it --rm \
     -v ~/hellopt-test/infer_mount:/input \
     -v ~/hellopt-test/output:/output \
     hello-pt bash
   ```
   Inside the container:
   ```bash
   python infer.py /output/model_parameters.pt
   cat /output/dataset.csv   # should show a Model_Score column added
   ```
   You may see a `FutureWarning` about `torch.load` and `weights_only=False` - that's harmless here (it's a warning about loading untrusted files from the internet, not relevant to a model you just trained yourself) and doesn't stop the script from running. Check `dataset.csv` for the `Model_Score` column to confirm it actually completed.

   Type `exit` to leave the container.

6. Since `/input` and `/output` were mounted from your machine, the output is also visible on your host at `~/hellopt-test/output`.

## **Running this example on FCP**

`notebook.ipynb` walks through the whole FCP flow end-to-end: it authenticates, creates a project, registers the example's training data as a Dataset, creates the Code Object from your pushed image, trains, and downloads the resulting weights. It needs `rhino_health` installed (`pip install rhino_health`).

## **Cleanup**

**Locally:**
- Remove the local Docker image, if you built one: `docker rmi hello-pt`
- Remove the local test scratch directory: `rm -rf ~/hellopt-test`

**On FCP:** `notebook.ipynb` creates a new Project (with a Dataset and Code Object inside it) every time it runs. Its last cell is guarded behind a `CLEANUP = False` flag - set it to `True` and re-run that cell to remove them via the SDK once you're done. This does not delete the pushed container image from your registry.

## **Using a different Python or NVFlare version**

**This only applies to the local Docker walkthrough** - the "Running this example on FCP" flow must stay on NVFlare 2.6.0 regardless of Python version, per the constraint under "Requirements" above.

- If your local environment needs to stay on **Python 3.8**, use **NVFlare 2.4.2**, and keep `python:3.8-slim-bullseye` as the `Dockerfile` base image.
- For any other Python/NVFlare pairing, update the `nvflare==` line in `requirements.txt` and the base image in the `Dockerfile` accordingly, then re-run the local steps above to confirm training and inference both complete successfully.

## Getting Help
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
