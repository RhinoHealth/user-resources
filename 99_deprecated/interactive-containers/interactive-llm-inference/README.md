# Interactive Container Example - Interactive LLM Inference

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive LLM inference with Jupypter Notebook session to interact with remote data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive Jupyter Notebook
* Add links to the interactive desktop to load Jupyter Notebook
* Add a Jupyter Notebook to execute an LLM inference on the input files 
* Add a helper functions to be used by the Jupyter Notebook

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Interactive Container capability.

## How to Run Locally


### Prerequisites
- Create a Project
- `sftp` Data to Rhino Client
- Create an FCP Dataset
- Download a model + artifacts from HuggingFace: [Using the HuggingFace CLI to Download Models and Artifacts](https://huggingface.co/docs/huggingface_hub/main/en/guides/cli)
- Upload the model + artifacts to AWS S3 to utilize the Runtime External Storage feature for Code Runs: [Using Rhino Utility to Upload Files to AWS S3](https://github.com/RhinoHealth/user-resources/blob/main/rhino-utils/upload-file-to-s3.sh)

## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs Jupyter Notebook and other dependencies
- `requirements.txt` - Libraries, packages, and modules required for the execution of Python scripts
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop` - Files for creating a desktop link to open Jupyter Notebook
- `llm_inference.ipynb` - Jupyter Notebook used for importing helper functions to perform inference with an LLM
- `rhino_inference_helpers.py` - Helper script with functions that are imported in Jupyter Notebook for performing inference with an LLM
- `input/`
  - `dataset.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a radiology report 


## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).