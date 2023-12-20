## Conducting an end-to-end ML project using multimodal data from multiple hospitals

![image info](https://drive.google.com/uc?export=view&id=1SkAZdWns-Xi8lxw7xQzRhc8jKsnOCfIL)

## Notebook 1: Import EHR and CXR Datasets
In this step, we gain experience in importing multimodal datasets onto the Rhino FCP. We will use MIMIC-IV as the source to create datasets from a database that hosts EHR data. In addition, we will load CXR DICOM images, which are linked to the EHR tables using a mapping lookup table.

## Notebook 2: Data Engineering to Harmonize 
In this step, the AI developer modifies their dataset so that the data schema and content matches that of the health system's dataset. The 'data schemas' of the two datasets are then compared to validate that the data has been adequately harmonized. In this step, the user will gain experience of using IGC Jupyter Notebook - to transform and harmonize raw clinical data tables into sets of patient features for downstream AI training and evaluation work.

In addition, the the DICOM files (chest x-rays) are converted to JPEG.

Notebook 2: https://github.com/RhinoHealth/experimental/blob/main/sandbox/example_1/ai_developer_workgroup/data_harmonization.ipynb

## Notebook 3: Exploratory data analysis & biostatistical methods
In this step, the user will gain experience using privacy preserving exploratory data analytics capabilities of Rhino. We show few privacy preserving query with metrics.

## Step 4: Visualize Chest X-Rays for Quality Review
Interactive Containers: Show 3D Slicer viewer for X-Ray data - 3D Slicer Container - for data quality checks.

## Notebook 4: Execute Data Harmonization
Before applying data harmonization and featurization, create data splits at both sites. Partition the dataset by randomly allocating records into the training and test. It is common practice to allocate all records for each individual patient to separate data splits, in order to test for generalizability across unseen patients and to avoid information leakage. Assigning 80% of the data to the training split, 20% to the test split is a reasonable choice.

Create a container to run the training-test split and execute before running the data harmonization and patient featurization step.

Then, containerize the data harmonization code from step #2 using - one per site, and run the same against the whole site datasets to produce a patient table per site per split

## Step 6: Prepare Models for FL Training and execute model training
In this step, the user will gain experience converting an existing model to NVFlare and execute the FL model training across two sites. 

## Step 7: Federated Evaluations
Visualize evaluation results


Need Help?
[Rhino Health Documenation Center](https://docs.rhinohealth.com/) or [support@rhinohealth.com](mailto:support@rhinohealth.com)