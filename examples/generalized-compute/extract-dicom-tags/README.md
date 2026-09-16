# Generalized Compute Example - Extract DICOM Tags

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely extract data from DICOM tags into an output dataset on a Rhino Client.

**It shows how to:**
* Read dynamic run parameters provided when triggering the run of this code
* Process input DICOM data
* Create output CSV data from this input
* Use a single-step Dockerfile to build the container image (without using a separate step for installing requirements)

## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `extract_dicom_tags.py` - This file contains the python code for extracting the DICOM tags from the input files into an output dataset
- `requirements.in` - The input python requirements for this project
- `requirements.txt` - The compiled python requirements for this project (using `pip-compile` on the requirements.in file)

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
