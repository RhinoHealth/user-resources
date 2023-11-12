# NVIDIA FLARE Example - Quantile Regression
<br/>

### **Description**

This example uses NVIDIA FLARE v2.3 to fit a quantile regression model using Rhino Health's Federated Computing Platform (FCP)

It shows how to:
* Use sklearn with NVIDIA FLARE (NVFlare) v2.3 to fit a quantile regression model on FCP
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>


### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config
  - `feature_columns`: The list of columns to use as features for the quantile regression.
  - `label_column`: The column to use as the label for the quantile regression.
  - `config_fed_server.json` - The standard NVFlare federated server config
    - `quantile`: The quantile to use for the quantile regression. The default is 0.5 (the median)
    - `n_classes`: The number of classes to use for the quantile regression. The default is 1.
    - `alpha`: The alpha value to use for the quantile regression.
    - `solver`: The solver to use for the quantile regression. The default is "highs".
    - `fit_intercept`: Whether to fit an intercept for the quantile regression. The default is True.
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project when building with pip
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
