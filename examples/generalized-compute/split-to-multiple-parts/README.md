# Generalized Compute Example - Split To Multiple Parts

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely split an input dataset into an arbitrary number of output datasets on a Rhino Client.

The Code Object to use with this code should have one input (not marked as "List") and one output that is marked as "List".

When running this Code Object, pass in a run-time parameter called "num_parts" to configure the number of output parts. For example: `{"num_parts": 4}` will split the input dataset into 4 parts. The code has a default value of 3 parts to be used if no "num_parts" parameter is provided.

**It shows how to:**
* Process an input CSV file as a dataframe
* Create multiple output CSV files from this input
* Use a multi-step Dockerfile to build the container image (using a separate step for installing requirements)

## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `requirements.txt` - The python requirements for this project
- `split_dataset.py` - This file contains the python code for splitting input dataset (using numpy.array_split)

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
