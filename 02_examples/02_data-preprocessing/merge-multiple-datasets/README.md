# Generalized Compute Example - Merge Multiple Datasets
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely merge any number of input datasets into a single output dataset on a Rhino Client.

The Code Object to use with this code should have one input that is marked as "List" and one output (not marked as "List").

It shows how to:
* Process an arbitrary number of input CSV files
* Merge the inputs into a single output CSV file
* Use a single-step Dockerfile to build the container image (without using a separate step for installing requirements)

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `merge_multiple_datasets.py` - This file contains the python code for merging the input datasets
- `requirements.in` - The input python requirements for this project
- `requirements.txt` - The compiled python requirements for this project (using `pip-compile` on the requirements.in file)
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
