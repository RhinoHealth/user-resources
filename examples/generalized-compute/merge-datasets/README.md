# Generalized Compute Example - Merge Datasets

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely merge two input datasets into a single output dataset on a Rhino Client.

**It shows how to:**
* Process multiple input CSV files
* Merge the inputs into a single output CSV file
* Use a single-step Dockerfile to build the container image (without using a separate step for installing requirements)

## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `merge_datasets.py` - This file contains the python code for merging the input datasets
- `requirements.in` - The input python requirements for this project
- `requirements.txt` - The compiled python requirements for this project (using `pip-compile` on the requirements.in file)

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

