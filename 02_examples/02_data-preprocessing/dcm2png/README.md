# Generalized Compute Example - DICOM to png
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely transform DICOM files to png files on a Rhino Client.

It shows how to:
* Process CSV and DICOM files as inputs
* Produce CSV, DICOM, and other files as outputs
* Run multi-step code (executing multiple python files sequentially)

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `dcm2png.py` - This file contains the python code for converting DICOM to png
- `merge_manifest.py` - This file contains python code for matching the input DICOM to the output png files in the output manifest (csv) file
- `runprep.sh` - The entrypoint shell script for the docker container, which runs dcm2png.py and then merge_manifest.py
- `requirements.txt` - The python requirements for this project
- `input/`
  - `dataset.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a patient. For each patient, there is a DICOM series UID and the related metadata for this patient.
  - `dicom_data/` - This folder contains the DICOM imaging files, specifically chest X-ray (CXR) images, referenced in the dataset.csv file.
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
