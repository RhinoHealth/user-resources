# NVIDIA FLARE Example - Using Flower with NVIDIA FLARE v2.5

## Description

This example demonstrates the integration of Flower with NVFlare on Rhino's Federated Computing Platform (FCP). It shows how to train a PyTorch model in a federated learning setup, leveraging Flower for the federated learning framework and NVFlare for orchestration on the FCP.

**It includes:**
- A federated learning setup with Flower, utilizing custom model code.
- A script to perform inference on the trained model (infer.py).
- Packaging the code into a Docker container for use on FCP.

## Resources
- `app/`: Contains the application code for federated learning.
  - `config/`: NVFlare Configuration files for the federated client and server.
    - `config_fed_client.json`: The standard NVFlare federated client config.
    - `config_fed_server.json`: The standard NVFlare federated server config.
  - `custom/`: Custom Flower application code, including client and server setup, strategy, and task files.
    - `flwr_pt/`: Contains the federated learning code using Flower and PyTorch.
      - `client.py`: Defines the client logic for federated learning.
      - `server.py`: Defines the server logic and strategy for federated learning.
      - `strategy.py`: Implements the custom federated strategy, including saving model checkpoints.
      - `task.py`: Defines the model architecture and data loading functions.
    - `pyproject.toml`: The Flower project configuration.
- `Dockerfile` : A Dockerfile for building the container image, configured for use with FCP.
- `infer.py`: A script for running inference on the trained model.
- `meta.json`: Metadata about the project.
- `nvflare.patch`: A patch file for NVFlare to support Flower integration.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
