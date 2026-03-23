# Interactive Container Example - Interactive Jupyter Notebook

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive Jupypter Notebook session to interact with remote data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive Jupyter Notebook
* Add links to the interactive desktop to load Jupyter Notebook
* Add a script to create a manifest CSV file from the Jupyter Notebook output files

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Interactive Container capability.

## How to Run Locally



## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs Jupyter Notebook and other dependencies 
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop` - Files for creating a desktop link to open Jupyter Notebook
- `create_dataset_csv.py` - A script to create a manifest CSV file from the 3D Slicer output files
- `Rhino-Health-Logo.svg`, `Create-Output-Dataset.desktop`, `Create-Output-Dataset-link.desktop` - Files for creating a desktop link to run the create_dataset_csv.py script


## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
