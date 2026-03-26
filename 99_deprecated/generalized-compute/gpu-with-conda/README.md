# Generalized Compute Example - GPU With Conda
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely execute code that uses a GPU using conda on a Rhino Client.

It shows how to:
* Perform operations with cudf using GPUs in remotely executed code
* Use a conda base image and environment.yml when building a container image

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image, using a cuda base image from NVIDIA. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `cudf_preprocessing.py` - This file contains python code that uses cudf operations utilizing GPUs
- `environment.yml` - The conda environment setup (including python requirements) for this project
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
