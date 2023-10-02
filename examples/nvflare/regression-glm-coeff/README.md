# NVIDIA FLARE Example - GLM Coefficient Estimation
<br/>

### **Description**

This example contains files to train a GLM model to estimate coefficients for a regression model using Rhino Health's Federated Computing Platform (FCP) and NVIDIA FLARE (NVFLARE).
 
It shows how to:
* Get client's GLM coefficient estimations using NVFlare 
* Use any optimization method for aggregating each of the client's model parameters using NVFlare
* Package the code in a Docker container that can be used with FCP using pip

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 1 epoch for the example 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code for the regression model (reading the input data from the `/input` folder in order to work with FCP)
  - `coeff_optimizer.py` - The custom code used for optimizing and aggregate each client's results for the GLM coefficient estimation model. This code is used by the server to aggregate the results from each client by a known optimizing, and examples are provided for Nethon-Raphson (labeld as "NR") and Iteratively reweighted least squares (labeld as "IRLS") optimizers. 
- `Dockerfile` - This is the Dockerfile to be used for building the container image with pip
- `requirements.txt` - The python requirements for this project when building with pip
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).