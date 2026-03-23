# Generalized Compute Example - Extract DICOM Tags
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely extract data from DICOM tags into an output dataset on a Rhino Client.

It shows how to:
* Read dynamic run parameters provided when triggering the run of this code
* Process input DICOM data
* Create output CSV data from this input
* Use a single-step Dockerfile to build the container image (without using a separate step for installing requirements)

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image
- `extract_dicom_tags.py` - This file contains the python code for extracting the DICOM tags from the input files into an output dataset
- `requirements.in` - The input python requirements for this project
- `requirements.txt` - The compiled python requirements for this project (using `pip-compile` on the requirements.in file)
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
