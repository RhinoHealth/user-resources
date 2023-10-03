# NVIDIA FLARE Example - GLM Coefficient Estimation
<br/>

### **Description**

This example contains files to train a GLM model to estimate coefficients for a regression model using Rhino Health's Federated Computing Platform (FCP) and NVIDIA FLARE (NVFLARE).
 
It shows how to:
* Get client's GLM coefficient estimations using NVFlare 
* Use an optimization method for aggregating each of the client's model parameters using NVFlare (with the examples of Newton-Raphson and Iteratively Reweighted Least Squares (IRLS) optimizers)
* Package the code in a Docker container that can be used with FCP using pip

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config.
    - `glm_type`: The GLM family type (e.g. Binomial, Gaussian, Poisson, etc.). The default in "Binomial".
    - `method`: The optimization method to be used for aggregating the results from each client. The default is "IRLS" (another supported method is "NR" for Newton-Raphson optimization).
    - `offset`: The offset variable name for the poisson regression (Use this only when configuring "glm_type: Poisson").
    - `formula`: The formula for the GLM model, using a format like "y ~ x1 + x2 + x3 + ..." where y is the dependent variable and x1, x2, x3, ... are the independent variables. `formula` should not be used if `y_values` and `x_values` are used.
    - `x_values`: List of x values to use in the model. Should always be used with `y_values`. Should not be used if `formula` is used`.
    - `y_values`: List of the y values to use in the model. Should always be used with `x_values`. Should not be used if `formula` is used`.
  - `config_fed_server.json` - The standard NVFlare federated server config.
- `custom` - This is the standard NVFlare directory for custom model code, containing the code for the regression model (reading the input data from the `/input` folder in order to work with FCP)
  - `coeff_optimizer.py` - The custom code used for optimizing and aggregate each client's results for the GLM coefficient estimation model. This code is used by the server to aggregate the results from each client by a known optimizing, and examples are provided for Newton-Raphson (labeled as "NR") and IRLS. 
- `Dockerfile` - This is the Dockerfile to be used for building the container image with pip
- `requirements.txt` - The python requirements for this project when building with pip
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).