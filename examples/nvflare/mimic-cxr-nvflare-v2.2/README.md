# NVIDIA FLARE Example - MIMIC CXR for NVIDIA FLARE 2.2

## Description

This example contains files to train a pneumonia detection model from Chest XRays using Rhino's Federated Computing Platform (FCP) and NVIDIA FLARE v2.2

**It shows how to:**
* Use PyTorch model code adapted to NVIDIA FLARE (NVFlare) v2.2, and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

## Resources
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 1 epoch for the example 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code for the pneumonia model (reading the input data from the `/input` folder in order to work with FCP)
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `infer.py` - A script for running inference on the trained model
- `requirements.txt` - The python requirements for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

