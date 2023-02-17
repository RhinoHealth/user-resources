# Tutorial 1 -  Rhino Health Platform “Hello World” - Basic Usage
<br/>

### **Description**

By following the step-by-step instructions in this tutorial, you will learn how to:

1. Set up a new project
2. Prepare data, import it as a cohort, and explore data metrics.
3. Containerize your code and run it using our distributed computing platform.
4. Produce visualizations of the results and create a report in the project.
<br/><br/>

### **Resources**
1. `cohort.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a case (meaning study, or patient). For each case, there is a DICOM series UID, which is similar to a file path, and the related metadata as described in the schema. 
2. `data-prep/` - This folder contains a python script (dataprep_gc.py), and several additional files required to create the docker container that will run the script on the Rhino Health Platform (to be used in Step 5).
3. `dicom_data/` - This folder contains the DICOM imaging files, specifically chest X-ray (CXR) images, referenced in the cohort.csv file. When using files as input for your project, it is best practice to keep the files in a dedicated folder separate from the cohort.csv file.
4. `gc-docker-utils/` - This folder contains several utilities provided by Rhino Health to make the containerization of your code as simple as possible (to be used in steps 5 and 6).
5. `Pneumonia Input Schema.csv` - This schema is how you can tell the Rhino Health Platform what structure it should expect your data to be in. For this “Hello World” project, your data will contain:
    - **Radiology imaging data** - in DICOM format (.dcm files)
    - **Gender** - limited by the schema parameters to [M, F, O]
    - **Height** - in meters, limited by the schema to values between 0 and 2.3
    - **Weight** - in kg
    - **Boolean Pneumonia label** - ground truth for the classification
6. `Pneumonia Results Schema.csv` - a pre-defined output schema for the federated training example to be used in Step 6.
7. `prediction-model/` - this folder contains code for a federated learning (FL) model. The model utilizes PyTorch and has been wrapped for NVFlare (Nvidia’s FL framework. Additionally, the folder contained the files required to create the docker container that will run the model training on the Rhino Health Platform (to be used in Step 6 below).
9. `Tutorial 1 - results analysis notebook.ipynb` - this jupyter notebook is a step-by-step tutorial for producing model results visualizations using the Rhino Health Python SDK.

### Getting Help
Please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com) if you encounter any issues while following this tutorial.