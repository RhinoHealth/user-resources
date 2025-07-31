# NVIDIA FLARE Example - MIMIC CXR with NVIDIA FLARE v2.6 Client API
<br/>

### **Description**

This example contains files to train a pneumonia detection model from Chest X-rays using Rhino Health's Federated Computing Platform (FCP) and NVIDIA FLARE v2.6 with the modern Client API.

It shows how to:
* Use the new NVIDIA FLARE v2.6 Client API (`import nvflare.client as flare`) for cleaner, more intuitive federated learning code
* Convert PyTorch model code to federated learning with minimal changes using the modern API
* Add an `infer.py` script to enable automatic inference after training on a separate validation dataset
* Store model parameters in the standard format compatible with FCP inference
* Package the code in a Docker container that can be used with FCP
* Maintain compatibility with existing JSON configuration patterns

Please reference to the [tutorial](https://docs.rhinohealth.com/hc/en-us/articles/8088478664349-Tutorial-1-Basic-Usage) for in depth explanations on how to use NVFLARE on FCP.

### **Resources**
- `app/config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - Updated federated client config using ClientAPILauncherExecutor for the new client API
  - `config_fed_server.json` - Standard federated server config with model persistence to `/output/model_parameters.pt`
- `app/custom` - This is the standard NVFlare directory for custom model code
  - `__init__.py` - Python package initialization file
  - `network.py` - Pneumonia model definition
  - `pneumonia_fl_client_api.py` - Main training script using the new Client API (`import nvflare.client as flare`)
  - `pneumonia_trainer.py` - Alternative trainer implementation
  - `pt_constants.py` - PyTorch constants and configuration
  - `pt_model_locator.py` - Model locator for server-side operations
- `infer.py` - Inference script compatible with both old and new client API model formats
- `meta.conf` - Metadata configuration file
- `Dockerfile` - Dockerfile for building the container image
- `requirements.txt` - Python dependencies for NVIDIA FLARE v2.6
<br><br>

### **Key Features of New Client API**

The new NVIDIA FLARE v2.6 Client API provides:
- **Simplified federated learning loop** with `flare.receive()` and `flare.send()`
- **Cleaner code structure** compared to traditional executor approach
- **Built-in model format handling** with automatic PyTorch state_dict management
- **Easy metrics tracking** with the FLModel object
- **Backward compatibility** with existing FCP infrastructure

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
