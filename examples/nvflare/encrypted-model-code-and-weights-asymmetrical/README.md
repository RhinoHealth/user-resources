# NVIDIA FLARE Example - Encrypted Model Code and Weights
<br/>

### **Description**

This example shows how to security train a model using Rhino Health's Federated Computing Platform (FCP), encrypting both the model code and the model weights using a key known only to the person running the code

It shows how to:
* Locally encrypt your model code (in this example the model network architecture)
* Build a container image using just the encrypted code (and not the source code)
* Encrypt the model parameters so that they are stored in an encrypted manner on FCP
* Add an `infer.py` script to perform inference on the trained model, decrypting the model parameters during inference using a key provided during run time

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting 1 epoch in this example
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model parameters file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code
  - `decrypt_code.py` - A script for decrypting the code using a run time secret provided when triggering model training
  - `pneumonia_trainer.py` - The regular model code, in this case a PyTorch model for detecting pneumonia from CXR data, reading the input data from the `/input` folder in order to work with FCP
  - `pt_constants.py` - The regular constants for PyTorch training
  - `pt_secured_model_persistor.py` - A Persistor that encrypts the model weights before storing them using the `cryptography.fernet` python library
  - `network.py.enc` - An example of an encrypted `network.py` file (replace this with an encrypted file that you have the key for)
- `network.py` - The standard PyTorch network architecture file usually located within the `custom` directory, but included here because in this example it will be encrypted and will not be included in the container image in its raw format
- `encrypt_code` - Utilities for encrypting code using the `cryptography.fernet` python library
  - `generate_key.py` - A script for generating a new encryption key using the python cryptography.fernet library
  - `encrypt_code.py` - A script for encrypting input code with an input encryption key using the python cryptography.fernet library
- `entrypoint.sh` - A shell script to be used as the entrypoint for the containers, decrypting the encrypted code using a decryption key provided during run time
- `infer.py` - A script for running inference on the trained model, adapted to decrypt the model weights using a decryption key provided during run time
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project
<br><br>

### **Instructions**
1. Generate a new encryption key to be used for this code - it is stored locally so only you have access to this key: `python ./encrypt_code/generate_key.py ~/myprecious`
2. Encrypt the model code (in our example `network.py`, but you can also do this for multiple files) using the encryption key: `python ./encrypt_code/encrypt_code.py ./network.py ~/myprecious ./custom/network.py.enc`
3. (Optional) You can now delete the `network.py` file (or move it to a different directory) - it will not be used when building the container image, but if you want to validate this you can delete/move this file
4. Build the container image from the Dockerfile: `../../../rhino-utils/docker-push.sh rhino-gc-workgroup-my-workgroup pneumonia-prediction-secure`
5. Create a Model object in FCP using this container image in the Rhino Health UI or via the SDK
6. Use the following SDK code to execute training.
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
* secrets_fed_client contains the key sent to the federated client and is available to the containerized code at `/input/secret_run_params.json`
* secrets_fed_server contains the key sent to the federated server and is available to the containerized code at `/server-credentials/secret_run_params.json`
 
# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
