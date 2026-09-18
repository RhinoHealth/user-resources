# NVIDIA FLARE Example - XGBoost w/ Full Homomorphic Encryption

## Description
This example contains files to train an XGBoost model with full homomorphic encryption using Rhino's Federated Computing Platform (FCP) and NVFlare 2.5.

It is based on the NVFLare implementation of [federated secure XGBoost](https://github.com/NVIDIA/NVFlare/tree/2.5/examples/advanced/xgboost_secure) using the NVFlare encryption plugin.

The code can be run out of the box on the datasets provided in the [XGBoost Advanced Tutorial](../../../../tutorials/advanced/federated-training/xgboost-horizontal/data).

## Resources
- `app` - This is the standard NVFlare directory for containing NVFlare configs and custom code
  - `config` - This is the standard NVFlare directory for config files
    - `config_fed_client.json` - The standard NVFlare federated client config 
    - `config_fed_server.json` - The standard NVFlare federated server config, setting `secure_training` to `True`
  - `custom` - This is the standard NVFlare directory for custom model code, containing the code for the XGBoost data loader (reading the input data from the `/input` folder in order to work with FCP)
- `vendor`
  - `encryption_plugins` - These are the encryption plugins [provided by NVFlare](https://github.com/NVIDIA/NVFlare/tree/2.5/integration/xgboost/encryption_plugins). Note that we have by default disabled building the CUDA plugin.
- `Dockerfile` - This is the Dockerfile to be used for building the container image, including building the required encryption plugins
- `requirements.txt` - The python requirements for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).