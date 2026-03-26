# NVIDIA FLARE Example - Poisson Regression
<br/>

### **Description**

This example uses NVIDIA FLARE v2.3 to fit a poisson regression model using Rhino Health's Federated Computing Platform (FCP)

It shows how to:
* Use sklearn with NVIDIA FLARE (NVFlare) v2.3 to fit a poisson regression model on FCP
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `linear_config_fed_client.json` - The NVFlare federated client config for the linear regression model, reading input data from `/input`
  - `linear_config_fed_server.json` - The NVFlare federated server config for the linear regression model, writing global model parameters to `/output`
  - `logistic_config_fed_client.json` - The NVFlare federated client config for the logistic regression model, reading input data from `/input`
  - `logistic_config_fed_server.json` - The NVFlare federated server config for the logistic regression model, writing global model parameters to `/output`
- `custom` - This is the standard NVFlare directory for custom model code, containing the sklearn code for the model using an SGDClassifier for fitting
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
