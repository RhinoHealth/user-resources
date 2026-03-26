# Generalized Compute Example - GPU With Pip
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely execute code that uses a GPU using pip and cupy on a Rhino Client.

It shows how to:
* Perform operations with cupy using GPUs in remotely executed code

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `cupy_preprocessing.py` - This file contains python code that uses cupy operations utilizing GPUs
- `requirements.txt` - The python requirements for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
