# NVIDIA FLARE Example - Encrypted Model Code and Weights

*Last Updated: 2026-09-11*

## **Overview**

This example shows how to securely train a model using Rhino's Federated Computing Platform (FCP), encrypting both the model code and the model weights using a key known only to the person running the code.

It shows how to:
* Locally encrypt your model code (in this example the model network architecture)
* Build a container image using just the encrypted code (and not the source code)
* Encrypt the model parameters so that they are stored in an encrypted manner on FCP
* Add an `infer.py` script to perform inference on the trained model, decrypting the model parameters during inference using a key provided during run time

Please reference RhinoDocs for more info on how to use NVFlare on FCP:
- [Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference) (via UI)
- [Creating a New NVFlare Code Object](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk) (via SDK)
- [Running NVFlare Code](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk) (via SDK)

### **Requirements**

As noted in `requirements.txt`, this example uses **NVFlare 2.6.0**, **torch 2.4.0**, and **torchvision 0.19.0** on **Python 3.12**.

**NVFlare version must stay 2.6.0** for this example: FCP's server-side provisioning only has templates for NVFlare versions up to and including 2.6 (`CodeTypes.NVIDIA_FLARE_V2_6` is the newest available). A container pinned to a newer NVFlare (e.g. 2.7+/2.8.x) will fail with confusing, indirect errors - the client raises `RuntimeError: missing 'target' in server config ... the startup kit may have been provisioned with an older HA-based template`, and the server raises `ConfigError: ... Can't load class nvflare.app_common.logging.log_receiver.LogReceiver` - both symptoms of FCP generating a v2.6-era startup kit for a newer NVFlare that no longer matches it. This is unrelated to the local Docker walkthrough, which uses whatever NVFlare version is installed with no provisioning-template dependency, and can safely use newer NVFlare.

### **Repo Structure**
- `app` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config` - This is the standard NVFlare directory for config files
    - `config_fed_client.json` - The standard NVFlare federated client config, setting 1 epoch in this example
    - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model parameters file to be stored in `/output/model_parameters.pt.enc`
  - `custom` - This is the standard NVFlare directory for custom model code
    - `decrypt_code.py` - A script for decrypting the code using a run time secret provided when triggering model training
    - `network.py.enc` - An example of an encrypted `network.py` file (replace this with an encrypted file that you have the key for)
    - `pneumonia_trainer.py` - The regular model code, in this case a PyTorch model for detecting pneumonia from CXR data, reading the input data from the `/input` folder in order to work with FCP
    - `pt_constants.py` - The regular constants for PyTorch training
    - `pt_secured_model_persistor.py` - A Persistor that encrypts the model weights before storing them using the `cryptography.fernet` python library
- `data` - Small placeholder images (solid-color, synthetic) and matching CSVs, for local pipeline testing without needing real pneumonia CXR data (see steps 3 and 5 under "Running this example locally" for the commands to copy these into place)
  - `dataset_test.csv` - Labels/paths for the placeholder test images, copied in as `dataset.csv` during the inference setup steps below
  - `test` - Placeholder images used for the inference walkthrough
    - `NORMAL` - 5 placeholder images
    - `PNEUMONIA` - 5 placeholder images
  - `train` - Placeholder images used for the training walkthrough
    - `NORMAL` - 5 placeholder images
    - `PNEUMONIA` - 5 placeholder images
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `encrypt_code` - Utilities for encrypting code using the `cryptography.fernet` python library
  - `encrypt_code.py` - A script for encrypting input code with an input encryption key using the python cryptography.fernet library
  - `generate_key.py` - A script for generating a new encryption key using the python cryptography.fernet library
- `entrypoint.sh` - A shell script to be used as the entrypoint for the containers, decrypting the encrypted code using a decryption key provided during run time
- `infer.py` - A script for running inference on the trained model, adapted to decrypt the model weights using a decryption key provided during run time
- `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`) - required by FCP's provisioning for NVFlare >= 2.4 (see the version note above); FCP reads this straight from the running container, so it must exist at the container's WORKDIR regardless of `code_execution_mode`
- `network.py` - The standard PyTorch network architecture file usually located within the `custom` directory, but included here because in this example it will be encrypted and will not be included in the container image in its raw format
- `notebook.ipynb` - A runnable notebook for the "Running this example on FCP" walkthrough below - generates/encrypts the key, authenticates, registers data, creates the Code Object, trains, downloads the encrypted weights, and includes cleanup steps
- `README.md` - This file
- `requirements.txt` - The python requirements for this project

## **Running this example locally**

Unlike a standard NVFlare example, this one needs your own encryption key before anything else will run, since the shipped `network.py.enc` was encrypted with a key you don't have.

1. **Generate your own encryption key** and encrypt `network.py` with it (make sure you're running from the encrypted-model-code-and-weights directory):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install cryptography

   python encrypt_code/generate_key.py ~/myprecious
   python encrypt_code/encrypt_code.py network.py ~/myprecious app/custom/network.py.enc
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t hello-pt-secure .
   ```

3. **Set up training data and the secret key files.** The container looks for the key at `/input/secret_run_params.json` (client side) and `/server-credentials/secret_run_params.json` (server side) - FCP provides these automatically at runtime, but for a local test you create them yourself. `pneumonia_trainer.py` reads training data from `/input/datasets/<dataset_uid>/file_data`, matching the real per-dataset layout FCP's on-prem agent mounts for NVFlare training (unlike `infer.py`'s flat `/input/file_data`, which matches a different, single-dataset execution path) - so mount a fake dataset UID folder locally too:
   ```bash
   mkdir -p ~/pneumonia-test/train_mount/datasets/local-dataset/file_data
   cp -r data/train/NORMAL data/train/PNEUMONIA ~/pneumonia-test/train_mount/datasets/local-dataset/file_data/
   mkdir -p ~/pneumonia-test/output
   mkdir -p ~/pneumonia-test/server-credentials

   KEY=$(cat ~/myprecious)
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/train_mount/secret_run_params.json
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/server-credentials/secret_run_params.json
   ```
   This copies in the small placeholder images from `data/` (solid-color test images - fine for validating the pipeline mechanically). To use real pneumonia CXR data instead, swap in your own images in place of the placeholders.

4. **Run training:**
   ```bash
   docker run -it \
     -v ~/pneumonia-test/train_mount:/input \
     -v ~/pneumonia-test/output:/output \
     -v ~/pneumonia-test/server-credentials:/server-credentials \
     hello-pt-secure bash
   ```
   Inside the container:
   ```bash
   nvflare simulator -w /tmp/nvflare-workspace -n 1 -t 1 .
   ```
   You should see training complete with `Finished ScatterAndGather Training.`, and:
   ```bash
   ls -la /output   # should show model_parameters.pt.enc (encrypted)
   ```
   `exit` the container when done.

5. **Set up inference data**, including the same secret key file on the input side:
   ```bash
   mkdir -p ~/pneumonia-test/infer_mount/file_data
   cp -r data/test/NORMAL data/test/PNEUMONIA ~/pneumonia-test/infer_mount/file_data/
   cp data/dataset_test.csv ~/pneumonia-test/infer_mount/dataset.csv
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/infer_mount/secret_run_params.json
   ```
   This uses the placeholder test images and matching `dataset.csv` from `data/`. To use your own data, replace the images and update `dataset.csv` to reference them (`<class>/<filename>`).

6. **Run inference:**
   ```bash
   docker run -it \
     -v ~/pneumonia-test/infer_mount:/input \
     -v ~/pneumonia-test/output:/output \
     hello-pt-secure bash
   ```
   Inside the container:
   ```bash
   python infer.py /output/model_parameters.pt.enc
   cat /output/dataset.csv   # should show a Model_Score column added
   ```

## **Running this example on FCP**

`notebook.ipynb` runs the whole FCP flow end-to-end: it generates/encrypts the key, authenticates, creates a project, registers the placeholder training data as a Dataset, creates the Code Object, trains, downloads the encrypted weights, and includes an opt-in cleanup cell.

**Run the notebook** top to bottom, but treat the "Find your workgroup's container registry, then build and push the image" cell as a real pause point, not just another cell: you have to leave the notebook, run the build/push command it describes in a terminal, and come back with the printed URI before continuing. **The image must be (re)built after the "Generate and encrypt" cell above it has run**, using that exact `app/custom/network.py.enc` - an image built earlier, or from a different `~/myprecious`, bakes in a mismatched key. The container then crashes on decrypt before NVFlare ever starts, which surfaces only as a generic `NVFLARE server and clients failed to connect within 0:05:00` error with nothing more specific in the logs.

The notebook will walk you through each step (you'll be prompted for your password), printing progress along the way. On success it saves the trained, encrypted weights to `model_parameters.pt.enc`.


## **Cleanup**

**Locally:**
- `~/myprecious` is your encryption key - there is no way to recover the encrypted weights without it, so keep a copy somewhere safe before deleting it if you still need them.
- Both the local and FCP walkthroughs overwrite the tracked placeholder `app/custom/network.py.enc` with your own encrypted output. Check `git status` before committing anything in this directory; `git checkout -- app/custom/network.py.enc` restores the shipped placeholder. `model_parameters.pt.enc` is already git-ignored.
- Remove the local Docker image, if you built one: `docker rmi hello-pt-secure`
- Remove the local test scratch directory from the "Running this example locally" walkthrough: `rm -rf ~/pneumonia-test`
- (Optional) Delete the pushed image from your registry once you no longer need it, e.g. for ECR: `aws ecr batch-delete-image --repository-name <your-workgroup-repo-name> --image-ids imageTag=<tag>`

**On FCP:** `notebook.ipynb` creates a new Project (with a Dataset and Code Object inside it) every time it runs. Its last cell is guarded behind a `CLEANUP = False` flag - set it to `True` and re-run that cell to remove them via the SDK (`session.code_object.remove_code_object`, `session.dataset.remove_dataset`, `session.project.remove_project`) once you're done. This does not delete the pushed container image from your registry.

## **Under the Hood**
* The container image only includes the encrypted version of `network.py.enc` and not the original decrypted version
* When the federated client container initializes, the `entrypoint.sh` triggers `app/custom/decrypt_code.py` using the run-time secret key to decrypt the `network.py.enc` file and stores it as `app/custom/network.py`. Now training can commence as usual on the federated client side
* When weights are sent to the federated server, the `pt_secured_model_persistor.py` encrypts them using the provided run-time secret key before storing them in the `/output` folder
* During model inference, the `infer.py` script decrypts the model weights using the run-time secret key before performing inference

Notes:
* `secrets_fed_client` contains the key sent to the federated client and is available to the containerized code at `/input/secret_run_params.json`
* `secrets_fed_server` contains the key sent to the federated server and is available to the containerized code at `/server-credentials/secret_run_params.json`

## **Using a different Python or NVFlare version**

**This only applies to the local Docker walkthrough** - the "Running this example on FCP" flow must stay on NVFlare 2.6.0 regardless of Python version, per the constraint above.

If your local environment needs to stay on **Python 3.8**, NVFlare's own version constraints mean **NVFlare 2.4.2** is the highest compatible version - later releases either require Python ≥3.9 or have a known issue on Python 3.8. This has not been validated specifically for this example's PyTorch and cryptography dependencies; if you go this route, you will also need to pin compatible `torch`/`torchvision`/`cryptography` versions for Python 3.8 and re-run the steps above to confirm training and inference both complete successfully.

# Getting Help
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).