# Generalized Compute Example - Split To Multiple Parts
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely split an input dataset into an arbitrary number of output datasets on a Rhino Client.

The Code Object to use with this code should have one input (not marked as "List") and one output that is marked as "List".

When running this Code Object, pass in a run-time parameter called "num_parts" to configure the number of output parts. For example: `{"num_parts": 4}` will split the input dataset into 4 parts. The code has a default value of 3 parts to be used if no "num_parts" parameter is provided.

It shows how to:
* Process an input CSV file as a dataframe
* Create multiple output CSV files from this input
* Use a multi-step Dockerfile to build the container image (using a separate step for installing requirements)

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `split_dataset.py` - This file contains the python code for splitting input dataset (using numpy.array_split)
- `requirements.txt` - The python requirements for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
