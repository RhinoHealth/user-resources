# NVIDIA FLARE Example - Hello PyTorch
<br/>

### **Description**

This example adapts NVIDIA's [Hello PyTorch](https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-pt) NVIDIA FLARE example to run on Rhino Health's Federated Computing Platform (FCP).

It shows how to:
* Use PyTorch model code adapted to NVIDIA FLARE (NVFlare), and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 4 epochs for the example 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA examples, but with the inputs being read from the `/input` folder in order to work with FCP
- `data` - A folder with some example data to train/test with
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `infer.py` - A script for running inference on the trained model
- `requirements.txt` - The python requirements for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
