# Rhino Health Examples - Generalized Compute
This folder contains examples for using Rhino Health's Generalized Compute capability

## Table of Contents
- [dcm2png](./dcm2png/README.md) - Process input CSV and DICOM files and transform the DICOM to png format, storing CSV, DICOM, and other files as outputs. This is runs multi-step code (executing multiple python files sequentially) 
- [extract-dicom-tags](./extract-dicom-tags/README.md) - Process input CSV and DICOM files and extract DICOM tags from the input, storing these in the output CSV file. Read the list of tags from a dynamic run-time parameter
- [gpu-with-conda](./gpu-with-conda/README.md) - Perform operations with cudf using GPUs in remotely executed code, building the container image using conda
- [gpu-with-pip](./gpu-with-pip/README.md) - Perform operations with cupy using GPUs in remotely executed code
- [merge-datasets](merge-datasets/README.md) - Process two input CSVs and merge them into one output CSV
- [merge-multiple-datasets](merge-multiple-datasets/README.md) - Process an arbitrary number of input CSVs and merge them into one output CSV
- [run-encrypted-code](./run-encrypted-code/README.md) - Locally encrypt the code that you would like to have run and build a container image using just the encrypted code (and not the source code). Have the container execute the encrypted code, using the decryption key as an input parameter provided during run time
- [split-to-multiple-parts](./split-to-multiple-parts/README.md) - Process an input CSV and split it into an arbitrary number of output CSVs, based on a run-time parameter
- [train-test-split](./train-test-split/README.md) - Process an input CSV and split it into two output CSVs

## How to build and push Generalized Compute Containers
Prior to running these interactive containers remotely on a Rhino client, the containers will need to be built locally and then uploaded to Amazon Elastic Container Registry (ECR). If you haven't done so already, you should [Configure Your Environment](https://docs.rhinohealth.com/hc/en-us/articles/12385555709085-Configuring-your-Environment) in order to push code to ECR.

Once you've succesfully configured your environment, we recommending using [Rhino's utilities](../../rhino-utils/) to assist in building container images and pushing them to ECR. 

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
