# Generalized Compute Example - GPU With Conda

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely execute code that uses a GPU using conda on a Rhino Client.

**It shows how to:**
* Perform operations with cudf using GPUs in remotely executed code
* Use a conda base image and environment.yml when building a container image

## Resources
- `cudf_preprocessing.py` - This file contains python code that uses cudf operations utilizing GPUs
- `Dockerfile` - This is the Dockerfile to be used for building the container image, using a cuda base image from NVIDIA. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `environment.yml` - The conda environment setup (including python requirements) for this project

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

