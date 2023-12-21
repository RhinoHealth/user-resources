## Conducting an end-to-end ML project using multimodal data from multiple hospitals

![image info](https://drive.google.com/uc?export=view&id=1SkAZdWns-Xi8lxw7xQzRhc8jKsnOCfIL)

### Step 0: Create a project in the Rhino web platform

Log in at https://dashboard.rhinohealth.com/login. If this is your first time logging in, you will be required to change your initial password and sign the EULA. 

Create a new project by clicking on the Add New Project button in the top right corner.

Fill in the following fields within the new modal window:

- **Name**: Federated Datasets and Predictive Modeling
- **Description**: Federated Datasets and Predictive Modeling
- **Permission Policy**: Expand this section to explore the various configurable permission policies and personas that are available to you. For this tutorial, you can leave the default permission policy.
Click the Create Project button to create your project. Once clicked, you will be navigated back to the project screen where you will see your newly created project.
- **Collaborators** - Click Collaborators symbol and add "Health System - Sandbox" as collaborator. You will receive approval in few minutes. The "Health System - Sandbox" owner will import additional dataset in your project. Now, you can use datasets from Health System node on top of datasets available in your data node.

We simulate having datasets from multiple organizations (also called the “cross-silo” setting in federated learning) by splitting the original MIMIC dataset into multiple partitions. Each partition will represent the data from a single organization. We’re doing this purely for experimentation purposes, in the real world there’s no need for data splitting because each organization already has their own data (so the data is naturally partitioned).

## Notebook 1: Import EHR and CXR Datasets
In this step, we gain experience in importing multimodal datasets onto the Rhino FCP. We will use MIMIC-IV as the source to create datasets from a database that hosts EHR data. In addition, we will load CXR DICOM images, which are linked to the EHR tables using a mapping lookup table.

## Notebook 2: Data Engineering 
 In this step, the the DICOM files (chest x-rays) are converted to JPEG.

## Notebook 3: Exploratory data analysis & biostatistical methods
In this step, the user will gain experience using privacy preserving exploratory data analytics capabilities of Rhino. We show few privacy preserving query with metrics.


## Notebook 4: Prepare Models for FL Training and execute model training
In this step, you will split data into training and testing and use the datasets for model training. You will gain experience converting an existing model to NVFlare and execute the FL model training across two sites. 

## Notebook 5: Federated Evaluations
Visualize evaluation results


Need Help?
[Rhino Health Documenation Center](https://docs.rhinohealth.com/) or [support@rhinohealth.com](mailto:support@rhinohealth.com)