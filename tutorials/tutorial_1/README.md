# Tutorial #1 - Rhino Health Federated Computing Platform “Hello World” - Basic Usage
<br/>

### **Description**

By following the [step-by-step instructions](https://docs.rhinohealth.com/hc/en-us/articles/8088478664349-Tutorial-1-Rhino-Health-Federated-Computing-Platform-Hello-World-Basic-Usage) in this tutorial, you will learn how to:

1. Set up a new project
2. Prepare data, import it as a cohort, and explore data metrics.
3. Containerize your code and run it using our distributed computing platform.
4. Produce visualizations of the results and create a report in the project.
<br/><br/>

### **Resources**
- `containers/` - This directory contains folders for each of the containers you will use in this tutorial
  - `data-prep/` - This folder contains a python script (dataprep_gc.py), and several additional files required to create the docker container that will run the script on the RHP
  - `prediction-model/` - this folder contains code for a federated learning (FL) model. The model utilizes PyTorch and has been wrapped for NVFlare (Nvidia’s FL framework). Additionally, the folder contains the files required to create the docker container that will run the model training on the FCP
- `data/` - This directory contains the data that is need for the tutorial
  - `input/`
    - `cohort_data.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a case (meaning study, or patient). For each case, there is a DICOM series UID, which is similar to a file path, and the related metadata as described in the schema
    - `dicom_data/` - This folder contains the DICOM imaging files, specifically chest X-ray (CXR) images, referenced in the cohort_data.csv file. When using files as input for your project, it is best practice to keep the files in a dedicated folder separate from the cohort_data.csv file
- `notebooks/` - This folder contains the jupyter notebook you will use within this tutorial
  - `Tutorial 1 - Results Analysis Notebook.ipynb` - this jupyter notebook is a step-by-step tutorial for producing model results visualizations using the Rhino Health Python SDK
- `schemas/` - This folder contains the data schema you will need to complete this tutorial
  - `Pneumonia Input Schema.csv` - This is the schema for your input cohort. It is how you can tell the FCP what structure it should expect your data to be in
  - `Pneumonia Results Schema.csv` - The pre-defined output schema for the federated training example

<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).