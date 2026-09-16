# NVIDIA FLARE Example - MIMIC CXR with NVIDIA FLARE v2.5

## Description
This example contains files to train a pneumonia detection model from Chest XRays using Rhino's Federated Computing Platform (FCP) and NVIDIA FLARE v2.5.

**It shows how to:**
* Use PyTorch model code adapted to NVIDIA FLARE (NVFLARE) v2.4, with the necessary settings for it to run on FCP.
* Add an `infer.py` script enable automatic inference after training on a separate validation dataset.
* Log metrics using TensorBoard, both per-client and aggregated.  These may be viewed via FCP's integrated TensorBoard.
* Store model checkpoints throughout the training process.  These are all persisted on the FCP for your later use.
* Package the code in a Docker container that can be used with FCP.
* Use either pip or miniconda to install dependencies.

## Resources
- `app/config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 1 epoch for the example 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `app/custom` - This is the standard NVFlare directory for custom model code, containing the code for the pneumonia model (reading the input data from the `/input` folder in order to work with FCP)
- `Dockerfile` - Default Dockerfile for building the container image
- `infer.py` - A script for running inference on the trained model
- `requirements.txt` - The python dependencies for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
