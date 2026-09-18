# NVIDIA FLARE Example - MONAI Model Zoo - Spleen CT Segmentation

## Description
This example uses NVIDIA FLARE to perform federated training of a spleen CT segmentation model from the [Monai Model Zoo](https://monai.io/model-zoo.html) adapted to run on Rhino's Federated Computing Platform (FCP)

**It shows how to:**
* Use a model from the MONAI Model Zoo with NVIDIA FLARE (NVFlare) and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

## Resources
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 1 epoch for the example 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
  - `spleen_ct_segmentation` - The bundle from the MONAI Model Zoo for the spleen CT segmentation model
- `custom` - This is the standard NVFlare directory for custom model code
  - `rhino_client_algo_executor.py` - An adapted Executor to execute the model code within FCP 
  - `rhino_monai_bundle_persistor.py` - An adapted Persistor to store the model outputs in the `/output` directory
- `schemas` - input and output schemas for Monai datasets
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `infer.py` - A script for running inference on the trained model
- `requirements.txt` - The python requirements for this project

This example uses the Spleen CT Segmentation model from the MONAI Model Zoo, but the other models from the MONAI Model Zoo can also work with FCP

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
