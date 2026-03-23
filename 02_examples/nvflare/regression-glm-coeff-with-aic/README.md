# NVIDIA FLARE Example - Federated GLM with AIC-Based Feature Selection
<br/>

### **Description**

 
This example demonstrates how to fit a federated Generalized Linear Model (GLM) and perform Akaike Information Criterion (AIC)-based feature selection using Rhino's Federated Computing Platform (FCP) with NVIDIA FLARE (NVFLARE).


It shows how to:
* Fit a federated GLM to estimate coefficients and standard errors using NVFlare, supporting different GLM families (e.g. Binomial, Gaussian, Poisson, etc.)
* Apply AIC-based backward feature elimination to iteratively remove non-informative predictors and identify a more parsimonious model
* Use an optimization method for aggregating each of the client's model parameters using NVFlare (with the examples of Newton-Raphson and Iteratively Reweighted Least Squares (IRLS) optimizers)
* Read different configurations for the federated server and client from a config file, including the GLM family type, the optimization method, and the formula for the regression
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use NVFlare on FCP
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config
    - `glm_type`: The GLM family type (e.g. Binomial, Gaussian, Poisson, etc.). The default is "Binomial".
    - `method`: The optimization method to be used for aggregating the results from each client. The default is "IRLS" (another supported method is "NR" for Newton-Raphson optimization)
    - `offset`: The offset variable name for the poisson regression (Use this only when using "glm_type: Poisson")
    - `formula`: The formula for the regression model, using a format like "y ~ x1 + x2 + x3 + ..." where y is the dependent variable and x1, x2, x3, ... are the independent variables. `formula` should not be used if `y_values` and `x_values` are used
    - `x_values`: List of x values to use in the model. Should always be used with `y_values`. Should not be used if `formula` is used`
    - `y_values`: List of the y values to use in the model. Should always be used with `x_values`. Should not be used if `formula` is used`
    - `cast_to_string_fields`: A list of fields to explicitly cast to string. This is useful for fields that are numeric but should be treated as categorical
    - `add_intercept`: Whether to explicitly add an intercept column to the data before fitting
  - `config_fed_server.json` - The standard NVFlare federated server config
    - `target_accuracy`: The level of accuracy after which the server will stop the federated learning process. The default is 1e-5 (0.00001)
- `custom` - This is the standard NVFlare directory for custom model code, containing the code for the regression model (reading the input data from the `/input` folder in order to work with FCP)
  - `coeff_optimizer.py` - The custom code used for optimizing and aggregate each client's results for the GLM coefficient estimation model. This code is used by the server to aggregate the results from each client by a known optimizing, and examples are provided for Newton-Raphson (labeled as "NR") and IRLS 
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project when building with pip
- `aic_user_example_notebook.ipynb` - A Jupyter notebook with an example of how to use the Rhino SDK to run an initial full GLM model, iteratively eliminate features based on AIC, track and store AIC scores across iterations, and identify the optimal feature subset in a federated environment.









<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
