# NVIDIA FLARE Example - Split Learning

## Description
This example adapts NVIDIA's [Split Learning](https://github.com/NVIDIA/NVFlare/tree/2.3/examples/advanced/vertical_federated_learning) NVIDIA FLARE example to run on Rhino's Federated Computing Platform (FCP).

**It shows how to:**
* Use PyTorch model code adapted to NVIDIA FLARE (NVFlare) v2.3, and apply the necessary changes for it to run on FCP
* Use split learning to train a model in a scenario where data is stored in one site and labels are stored in another site
* Package the code in a Docker container that can be used with FCP

## Resources
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config 
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA example, but with the inputs being read from the `/input` folder in order to work with FCP
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `requirements.txt` - The python requirements for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
