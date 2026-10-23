# Tutorial 1 -  Basic Usage of Rhino Federated Computing Platform (FCP) 
> Last validated: 2026-10-23

## Description

Contains the resources for Tutorial 1, that goes over how to configure a project, register data, and analyze it with basic metrics, visualizations, and reports.

See [RhinoDocs](https://docs.rhinofcp.com/tutorials-recipes-and-demos/tutorial-1-basic-usage) for additional info and instructions.

## Resources
- `containers/` - Folders for each of the containers you will build and run in this tutorial
  - `data-prep/` - A container that adds a BMI column, performs data imputation, and converts raw DICOM images into JPEGs, producing a prepared dataset that can be used for training
    - `dataprep_gc.py` - Reads `dataset.csv` and the referenced DICOM files from `/input`, converts each DICOM image to a JPEG, imputes missing tabular values, computes the BMI column, and writes the result to `/output`
    - `Dockerfile` - Builds the container image for the data-prep script
    - `requirements.txt` - Python dependencies for `dataprep_gc.py`
    - `run_dataprep.sh` - Entrypoint script the container runs; wraps `dataprep_gc.py` with `--input_dir`/`--output_dir`/`--input_csv` arguments
  - `prediction-model/` - An NVFlare federated learning container that trains a PyTorch pneumonia-detection model on the prepared dataset. See this folder's own `README.md` for full detail.
    - `app/` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
      - `config/` - The standard NVFlare directory for config files
        - `config_fed_client.json` - Federated client config, using the NVFlare v2.6 Client API launcher
        - `config_fed_server.json` - Federated server config, including where trained model parameters are persisted
      - `custom/` - The standard NVFlare directory for custom model code
        - `network.py` - The PyTorch pneumonia model architecture definition
        - `pneumonia_fl_client_api.py` - The client-side training script, using NVFlare's v2.6 Client API (`import nvflare.client as flare`)
        - `rhino_pt_model_persistor.py` - Custom model persistor that saves a timestamped checkpoint file after every training round
    - `Dockerfile` - Builds the container image for federated training
    - `infer.py` - Runs inference with a trained model against a validation dataset
    - `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`)
    - `README.md` - This container's own, more detailed description
    - `requirements.txt` - Python dependencies for training (NVFlare, torch, torchvision, etc.)
- `data/` - The data used as input for this tutorial
  - `input/`
    - `dicom_data/` - The chest X-ray (CXR) DICOM imaging files referenced by `dataset.csv`, kept in their own folder separate from the tabular data, as is best practice
    - `dataset.csv` - Defines the original dataset used as input for this project. Each row represents a case (study/patient): a DICOM series UID (similar to a file path) plus the related metadata described in the input schema
- `notebooks/` - The Jupyter notebook used in this tutorial, plus the example plots it produces
  - `Gender_ROC.png` - Example output: combined ROC curves split out by gender
  - `Gender_ROC_F.png` - Example output: ROC curve for the female subgroup only
  - `Gender_ROC_M.png` - Example output: ROC curve for the male subgroup only
  - `Overall_ROC.png` - Example output: the overall ROC curve across all cases
  - `Overall_ROC_CI.png` - Example output: the overall ROC curve with a confidence interval band
  - `Tutorial 1 - Results Analysis Notebook.ipynb` - A step-by-step walkthrough for producing Code Run visualizations (including the plots above) using the Rhino Python SDK, and adding them to a project report
- `schemas/` - The data schemas needed to complete this tutorial
  - `Pneumonia Input Schema.csv` - The schema for your input dataset - how you tell FCP what structure to expect your data to be in
  - `Pneumonia Output Schema.csv` - The pre-defined output schema for the federated training example
- `README.md` - This file

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).