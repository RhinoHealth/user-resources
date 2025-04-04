# Rhino Health Examples - Generalized Compute
This folder contains examples for using Rhino Health's Generalized Compute capability

## Table of Contents
- [dcm2png](./dcm2png/README.md) - Process input CSV and DICOM files and transform the DICOM to png format, storing CSV, DICOM, and other files as outputs. This is runs multi-step code (executing multiple python files sequentially) 
- [extract-dicom-tags](./extract-dicom-tags/README.md) - Process input CSV and DICOM files and extract DICOM tags from the input, storing these in the output CSV file. Read the list of tags from a dynamic run-time parameter
- [gpu-with-conda](./gpu-with-conda/README.md) - Perform operations with cudf using GPUs in remotely executed code, building the container image using conda
- [gpu-with-pip](./gpu-with-pip/README.md) - Perform operations with cupy using GPUs in remotely executed code
- [run-encrypted-code](./run-encrypted-code/README.md) - Locally encrypt the code that you would like to have run and build a container image using just the encrypted code (and not the source code). Have the container execute the encrypted code, using the decryption key as an input parameter provided during run time

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
