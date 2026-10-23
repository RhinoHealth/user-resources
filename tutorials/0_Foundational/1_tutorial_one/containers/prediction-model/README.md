# Tutorial 1 - Prediction Model

## Description

This example trains a pneumonia detection model from chest X-rays using Rhino's Federated Computing Platform (FCP) and NVIDIA FLARE (NVFlare) v2.6 with the modern Client API.

It shows how to:
* Use the NVFlare v2.6 Client API (`import nvflare.client as flare`) for cleaner, more intuitive federated learning code
* Convert PyTorch model code to federated learning with minimal changes using the modern API
* Add an `infer.py` script to enable automatic inference after training on a separate validation dataset
* Store model parameters in the standard format compatible with FCP inference
* Package the code in a Docker container that can be used with FCP
* Maintain compatibility with existing JSON configuration patterns

## Resources
- `app/` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
  - `config/` - The standard NVFlare directory for config files
    - `config_fed_client.json` - Federated client config, using `ClientAPILauncherExecutor` for the Client API
    - `config_fed_server.json` - Federated server config, with model persistence to `/output/model_parameters.pt`
  - `custom/` - The standard NVFlare directory for custom model code
    - `network.py` - The PyTorch pneumonia model architecture definition
    - `pneumonia_fl_client_api.py` - The main training script, using the Client API (`import nvflare.client as flare`)
    - `rhino_pt_model_persistor.py` - Custom model persistor that saves a timestamped checkpoint file after every training round
- `Dockerfile` - Builds the container image
- `infer.py` - Inference script, compatible with both old and new Client API model formats
- `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`)
- `README.md` - This file
- `requirements.txt` - Python dependencies for NVFlare v2.6

## Key Features of the v2.6 Client API

The NVFlare v2.6 Client API provides:
- **Simplified federated learning loop** with `flare.receive()` and `flare.send()`
- **Cleaner code structure** compared to the traditional executor approach
- **Built-in model format handling** with automatic PyTorch `state_dict` management
- **Easy metrics tracking** with the `FLModel` object
- **Backward compatibility** with existing FCP infrastructure

# Getting Help
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
