# Generalized Compute Example - Train Test Split

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely split an input dataset into two output datasets on a Rhino Client.

**It shows how to:**
* Process an input CSV file as a dataframe
* Create multiple output CSV files from this input
* Use a multi-step Dockerfile to build the container image (using a separate step for installing requirements)

## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project
- `run_code.sh` - The entrypoint shell script for the docker container, which runs train_test_split.py 
- `train_test_split.py` - This file contains the python code for splitting input dataset (using sklearn.model_selection.train_test_split)

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
