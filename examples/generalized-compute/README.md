# Rhino Health Examples - Generalized Compute
This folder contains examples for using Rhino Health's Generalized Compute capability
<br>

# Table of Contents
- [dcm2png](./dcm2png/README.md) - Process input CSV and DICOM files and transform the DICOM to png format, storing CSV, DICOM, and other files as outputs. This is runs multi-step code (executing multiple python files sequentially) 
- [extract-dicom-tags](./extract-dicom-tags/README.md) - Process input CSV and DICOM files and extract DICOM tags from the input, storing these in the output CSV file. Read the list of tags from a dynamic run-time parameter
- [train-test-split](./train-test-split/README.md) - Process an input CSV and split it into two output CSVs
- [merge-cohorts-data](./merge-cohorts-data/README.md) - Process multiple input CSVs and merge them into one output CSV
- [gpu-with-pip](./gpu-with-pip/README.md) - Perform operations with cupy using GPUs in remotely executed code
- [gpu-with-conda](./gpu-with-conda/README.md) - Perform operations with cudf using GPUs in remotely executed code, building the container image using conda
- [run-encrypted-code](./run-encrypted-code/README.md) - Locally encrypt the code that you would like to have run and build a container image using just the encrypted code (and not the source code). Have the container execute the encrypted code, using the decryption key as an input parameter provided during run time
- [interactive-3d-slicer](./interactive-3d-slicer/README.md) - Run an interactive container session with 3D Slicer to view and/or annotate remote DICOM data on a Rhino Client
- [interactive-qupath](./interactive-qupath/README.md) - Run an interactive container session with QuPath to view and/or annotate remote DICOM data on a Rhino Client
- [interactive-jupyter-notebook](./interactive-jupyter-notebook/README.md) - Run an interactive container session with Jupyter Notebook to interact with remote data on a Rhino Client
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
