# Generalized Compute Example - DICOM to png

## Description
This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely transform DICOM files to png files on a Rhino Client.

**It shows how to:**
* Process CSV and DICOM files as inputs
* Produce CSV, DICOM, and other files as outputs
* Run multi-step code (executing multiple python files sequentially)

## Resources
- `input/`
  - `dataset.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a patient. For each patient, there is a DICOM series UID and the related metadata for this patient.
  - `dicom_data/` - This folder contains the DICOM imaging files, specifically chest X-ray (CXR) images, referenced in the dataset.csv file.
- `dcm2png.py` - This file contains the python code for converting DICOM to png
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a multi-step process - first building a base image for installing requirements, then using this to build the output image.
- `merge_manifest.py` - This file contains python code for matching the input DICOM to the output png files in the output manifest (csv) file
- `requirements.txt` - The python requirements for this project
- `runprep.sh` - The entrypoint shell script for the docker container, which runs dcm2png.py and then merge_manifest.py

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

