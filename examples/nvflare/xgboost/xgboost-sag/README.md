# NVIDIA FLARE Example - XGBoost
<br/>

### **Description**

This example contains files to train an XGBoost model using Rhino Health's Federated Computing Platform (FCP) and NVIDIA FLARE v2.3

It shows how to:
* Use XGBoost model code adapted to NVIDIA FLARE (NVFlare) v2.3, and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model parameters file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code for the XGBoost model (reading the input data from the `/input` folder in order to work with FCP)
- `infer.py` - A script for running inference on the trained model
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
