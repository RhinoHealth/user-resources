# Generalized Compute Example - GPU With Pip

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely execute code that uses a GPU using pip and cupy on a Rhino Client.

**It shows how to:**
* Perform operations with cupy using GPUs in remotely executed code

## Resources
- `cupy_preprocessing.py` - This file contains python code that uses cupy operations utilizing GPUs
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `requirements.txt` - The python requirements for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
