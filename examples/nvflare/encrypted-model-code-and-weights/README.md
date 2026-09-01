# NVIDIA FLARE Example - Encrypted Model Code and Weights

*Last Updated: 2026-09-01*

### **Overview**

This example shows how to securely train a model using Rhino's Federated Computing Platform (FCP), encrypting both the model code and the model weights using a key known only to the person running the code.

It shows how to:
* Locally encrypt your model code (in this example the model network architecture)
* Build a container image using just the encrypted code (and not the source code)
* Encrypt the model parameters so that they are stored in an encrypted manner on FCP
* Add an `infer.py` script to perform inference on the trained model, decrypting the model parameters during inference using a key provided during run time

Please reference the User Documentation and/or Tutorials for more info on how to use NVFlare on FCP:
- [Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference) (FCP UI)
- [Creating a New NVFlare Code Object Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk)
- [Running NVFlare Code Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk)

### **Requirements**

As noted in `requirements.txt`, this example uses **NVFlare 2.8.1**, **torch 2.4.0**, and **torchvision 0.19.0** on Python 3.12.

### **Repo Structure**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting 1 epoch in this example
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model parameters file to be stored in `/output/model_parameters.pt.enc`
- `custom` - This is the standard NVFlare directory for custom model code
  - `decrypt_code.py` - A script for decrypting the code using a run time secret provided when triggering model training
  - `network.py.enc` - An example of an encrypted `network.py` file (replace this with an encrypted file that you have the key for)
  - `pneumonia_trainer.py` - The regular model code, in this case a PyTorch model for detecting pneumonia from CXR data, reading the input data from the `/input` folder in order to work with FCP
  - `pt_constants.py` - The regular constants for PyTorch training
  - `pt_secured_model_persistor.py` - A Persistor that encrypts the model weights before storing them using the `cryptography.fernet` python library
- `encrypt_code` - Utilities for encrypting code using the `cryptography.fernet` python library
  - `encrypt_code.py` - A script for encrypting input code with an input encryption key using the python cryptography.fernet library
   - `generate_key.py` - A script for generating a new encryption key using the python cryptography.fernet library
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `entrypoint.sh` - A shell script to be used as the entrypoint for the containers, decrypting the encrypted code using a decryption key provided during run time
- `infer.py` - A script for running inference on the trained model, adapted to decrypt the model weights using a decryption key provided during run time
- `network.py` - The standard PyTorch network architecture file usually located within the `custom` directory, but included here because in this example it will be encrypted and will not be included in the container image in its raw format
- `README.md` - This file
- `requirements.txt` - The python requirements for this project

### **Running this example locally**

Unlike a standard NVFlare example, this one needs your own encryption key before anything else will run, since the shipped `network.py.enc` was encrypted with a key you don't have.

1. **Generate your own encryption key** and encrypt `network.py` with it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install cryptography

   python encrypt_code/generate_key.py ~/myprecious
   python encrypt_code/encrypt_code.py network.py ~/myprecious custom/network.py.enc
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t hello-pt-secure .
   ```

3. **Set up training data and the secret key files.** The container looks for the key at `/input/secret_run_params.json` (client side) and `/server-credentials/secret_run_params.json` (server side) - FCP provides these automatically at runtime, but for a local test you create them yourself:
   ```bash
   mkdir -p ~/pneumonia-test/train_mount/file_data/NORMAL
   mkdir -p ~/pneumonia-test/train_mount/file_data/PNEUMONIA
   mkdir -p ~/pneumonia-test/output
   mkdir -p ~/pneumonia-test/server-credentials

   KEY=$(cat ~/myprecious)
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/train_mount/secret_run_params.json
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/server-credentials/secret_run_params.json
   ```
   Add some images to the `NORMAL` and `PNEUMONIA` folders (any real `.jpg`/`.png` images work for testing the pipeline mechanically - the model doesn't need to have real predictive value).

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

5. **Set up inference data**, including a `dataset.csv` with an `image_name,category` header, and the same secret key file on the input side:
   ```bash
   mkdir -p ~/pneumonia-test/infer_mount/file_data/NORMAL ~/pneumonia-test/infer_mount/file_data/PNEUMONIA
   echo "{\"key\": \"$KEY\"}" > ~/pneumonia-test/infer_mount/secret_run_params.json
   ```
   Add test images to each class folder and reference them in `dataset.csv`.

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

### **Running this example on FCP**

1. Generate a new encryption key to be used for this code - it is stored locally so only you have access to this key: `python ./encrypt_code/generate_key.py ~/myprecious`
2. Encrypt the model code (in our example `network.py`, but you can also do this for multiple files) using the encryption key: `python ./encrypt_code/encrypt_code.py ./network.py ~/myprecious ./custom/network.py.enc`
3. (Optional) You can now delete the `network.py` file (or move it to a different directory) - it will not be used when building the container image, but if you want to validate this you can delete/move this file
4. Build and push the container image to your workgroup's container registry
5. Create a Code Object in FCP using this container image, via the FCP UI ([Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference)) or the SDK ([Creating a New NVFlare Code Object Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk))
6. Use the following SDK code to execute training ([Running NVFlare Code Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk)):
```python
import json
run_params = ModelTrainInput(
    code_object_uid="", # Change this
    input_dataset_uids=[], # Change this
    one_fl_client_per_dataset=True,
    validation_dataset_uids=[], # Change this
    validation_datasets_inference_suffix="", # Change this
    timeout_seconds=300,
    config_fed_server="",
    config_fed_client="",
    secrets_fed_client=json.dumps({"key":""}), # Add the value from ~/myprecious
    secrets_fed_server=json.dumps({"key":""}), # Add the value from ~/myprecious
)
```
7. After training has completed, you can download the encrypted weights in the Rhino Health UI or via the SDK

#### **Under the Hood**
* The container image only includes the encrypted version of `network.py.enc` and not the original decrypted version
* When the federated client container initializes, the `entrypoint.sh` triggers `custom/decrypt_code.py` using the run-time secret key to decrypt the `network.py.enc` file and stores it as `custom/network.py`. Now training can commence as usual on the federated client side
* When weights are sent to the federated server, the `pt_secured_model_persistor.py` encrypts them using the provided run-time secret key before storing them in the `/output` folder
* During model inference, the `infer.py` script decrypts the model weights using the run-time secret key before performing inference

Notes:
* `secrets_fed_client` contains the key sent to the federated client and is available to the containerized code at `/input/secret_run_params.json`
* `secrets_fed_server` contains the key sent to the federated server and is available to the containerized code at `/server-credentials/secret_run_params.json`

### **Using a different Python or NVFlare version**

If your environment needs to stay on **Python 3.8**, NVFlare's own version constraints (documented in the `hello-numpy-sag-rhino` example in this repo) mean **NVFlare 2.4.2** is the highest compatible version - later releases either require Python ≥3.9 or have a known issue on Python 3.8. This has not been validated specifically for this example's PyTorch and cryptography dependencies; if you go this route, you will also need to pin compatible `torch`/`torchvision`/`cryptography` versions for Python 3.8 and re-run the steps above to confirm training and inference both complete successfully.

# Getting Help
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).