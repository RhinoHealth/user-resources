# Rhino Health Examples - Interactive Containers

This folder contains examples for using Rhino Health's Interactive Containers capability.

## Preparing to Push Containers
Prior to running these interactive containers remotely on a Rhino client, the containers will need to be built locally and then uploaded to Amazon Elastic Container Registry (ECR). If you haven't done so already, you should [Configure Your Environment](https://docs.rhinohealth.com/hc/en-us/articles/12385555709085-Configuring-your-Environment) in order to push code to ECR.

Once you've succesfully configured your environment, we recommending using Rhino's utilities(../../rhino-utils/) to assist in building container images and pushing them to ECR. 

## Table of Contents
- [interactive-3d-slicer](./interactive-3d-slicer/README.md) - Run an interactive container session with 3D Slicer to view and/or annotate remote DICOM data on a Rhino Client
- [interactive-3d-slicer-with-extensions](./interactive-3d-slicer-with-extensions/README.md) - Run a custom interactive container session of 3D Slicer with extensions so a user can view and/or annotate remote DICOM data on a Rhino Client
- [interactive-qupath](./interactive-qupath/README.md) - Run an interactive container session with QuPath to view and/or annotate remote DICOM data on a Rhino Client
- [interactive-jupyter-notebook](./interactive-jupyter-notebook/README.md) - Run an interactive container session with Jupyter Notebook to interact with remote data on a Rhino Client
- [jupyter-notebook-and-ollama](./jupyter-notebook-and-ollama/README.md) - Interact with LLM models via open-interpreter and Ollama.
- [libre-office](./libre-office/README.md) - Use Office (e.g. spreadsheets) to interact with remote data on a Rhino Client.

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
