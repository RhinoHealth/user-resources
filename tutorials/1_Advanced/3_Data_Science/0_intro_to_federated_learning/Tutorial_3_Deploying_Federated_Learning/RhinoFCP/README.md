
# Federated Learning Using Rhino FCP

## Goal

In this section we discuss deploying Federated Learning on the Rhino FCP. The user will learn how to containerize their federated applications and deploy them within projects on the Rhino FCP, enabling real-world collaboration.

## Contents
We have prepared all the necessary files for this portion of the tutorial, however they have already mostly been created by the user during the NVFlare simulation portion of the tutorial. We will analyze the difference to solidify key changes required to move federated learning workflows from simulation development to real-world production.

### NVFlare Components
Within the `RhinoFCP/` directory there is an `app/` subdirectory as well as a `meta.json` file. These are both components specific to NVFlare, and during the simulation these files were automatically generated. They can be found in `nvflare_simulation/simulation/NVFlare_DeepChem_Simulation/`. The `meta.json` file is entirely the same, but the files within the `app/` directory contain some Rhino FCP specific difference.

#### `config_fed_client.json`
```json
# Simulation Config
"task_script_path": "deepchem_simulation_train.py"

# Rhino FCP Config
"task_script_path": "/home/localuser/app/custom/deepchem_fl_train.py"
```
The containerized version of the application will always contain the training script in `/home/localuser/app/custom/` so the configuration must reflect that.

#### `config_fed_server.json`
```json
# Simulation Config
"model":    {
            "path": "deepchem_simulation_train.ClassificationModel",
            "args": {}
            },
"global_model_file_name": "/.../nvflare_simulation/saved_models/local_simulation.pt"

# Rhino FCP Config
"model":    {
            "path": "deepchem_fl_train.ClassificationModel",
            "args": {}
            },
"global_model_file_name": "/output/model_parameters.pt"
```
The containerized version of the application will define `/home/localuser/app/custom` as the PYTHONPATH so the path to the model class should be relative to this. The Rhino FCP also makes global model weights accessible when saved to the volume mounted to `/output` and either saved as `model_parameters.pt` or any `.pt` file saved under `/output/model_parameters/`

Visit NVFlare [GitHub](https://github.com/NVIDIA/NVFlare/tree/cf702a39b3d0449d1b983973de5cde276597955b/nvflare) documentation for more information on component and configuration options.

### Training and Inference Components
The only changes necessary for the training and inference scripts between simulation and deployment are the paths defined for inputs and outputs.

#### `deepchem_fl_train.py`
```python
data_dirs = [x for x in TRAIN_DATA_DIR.iterdir() if x.resolve().is_dir()]
```
`TRAIN_DATA_DIR` is defined in `config.py` but within the containerized application it will always require the path to be `/input/datasets/`.

#### `infer.py`
```python
args = sys.argv[1:]
(MODEL_PARAMS_PATH,) = args
TEST_DATA_PATH = Path("/input/dataset.csv")
PREDS_PATH = Path("/output/dataset.csv")
```
Inference workflows on the Rhino FCP will always pass in the model weights path via a system arg and the input dataset via `/input/dataset.csv` as well as making the results available within the platform when saved to `/output/dataset.csv`.

### Other Components
There are other common files associated with deploying any federated learning applications the Rhino FCP.

#### `Dockerfile`
We have provided a template for containerizing a federated learning application. In most cases, this template will natively work with other applications as long as they follow the same directory structure as this `RhinoFCP/` directory. Common changes to fit specific projects may inclue altering the base image of the file, and importing other files necessary for compute.

#### `requirements.txt`
These are the python requirements which will be installed within your containerized application.

#### `docker-push.sh`
A script developed to allow convenient upload of docker images to your workgroup's ECR.

## Instructions
1. Create a project within the Rhino FCP - See [Creating a Project](https://docs.rhinohealth.com/hc/en-us/articles/12522043724957-Creating-a-New-Project)
2. Import the 4 datasets to the project. One for each client and the test dataset - See [Creating a Dataset](https://docs.rhinohealth.com/hc/en-us/articles/31357028507165-Creating-a-New-Dataset-in-the-Rhino-FCP-GUI-Importing-a-Dataset) and [Importing a Dataset from Network Storage](https://docs.rhinohealth.com/hc/en-us/articles/18246660924061-Importing-to-and-Exporting-Datasets-from-Your-Network-Storage) <br> Note: For this tutorial make sure to uncheck Sensitive Data when you import your dataset
3. Create the containerized application image
   ```bash
   cd RhinoFCP/
   ./docker-push.sh <your-workgroup-container-registry-name> <your-desired-container-tag>
   ```
   To obtain your workgroup's ECR name refer to [Pushing Containers to the ECR](https://docs.rhinohealth.com/hc/en-us/articles/12385603287325-Pushing-Containers-to-the-ECR)

   Further documentation on setting up your local environment to communicate with your workgroup's ECR can be found in [Configuring your Environment](https://docs.rhinohealth.com/hc/en-us/articles/12385555709085-Configuring-your-Environment)
4. Create the code object within your project - See [Creating NVFlare Code Objects](https://docs.rhinohealth.com/hc/en-us/articles/12522224013085-Creating-New-NVFlare-Code-or-Code-Version) and the specific configurations below
5. Launch the NVFlare training run within the project - See [Running NVFlare Code](https://docs.rhinohealth.com/hc/en-us/articles/12522228144669-Running-NVFlare-Code) and the specific configurations below

*Incase the user does not have access to docker, or is not comfortable with the image creation portion of this workflow, the Rhino FCP offers an alternative solution called auto-containerization. The instructions for this can be found below under the* **Auto-Containers** *section.*

### Specific Configurations
#### Creating the code object
* NVFLARE Version: 2.6
* Use "Existing container image" and select the one you uploaded in step 3

#### Running the code object
* TRAINING DATASETS: Select all 3 site's training datasets
* Check the "Simulated FL; one FL client per training dataset" box
  * Otherwise, all three datasets would be imported into a single client for training
* VALIDATION DATASETS: Select the test dataset
  * When an `infer.py` file and a validation dataset are available when an NVFlare training run is complete, inference will automatically start using the global model from the training.

## Outputs
NVFlare training runs will often consist of 1 or 2 outputs.

### Model Weights
Global model weights from NVFlare trainings are accessible to download locally.
* Navigate to the Code Runs tab of the project
* Find the NVFlare training run that contains the global model weights you would like to download
* Select the **&#8942;** icon on the right side of the code run
* Select Download model parameters (if this option does not appear, you may be selecting an inference run. Ensure the Type column of the code run you are selecting says **T**)
  * If only one set of global model weights were saved to `/output/model_parameters.pt` then download will begin automatically
  * If multiple sets of global model weights were saved to `/output/model_parameters/` then a drop-down menu will appear to select which weights you would like to download.

### Inference Results
If post training inference is conducted, the results will be saved and accessible from within the project in the Datasets tab. Depending on permissions, the results may be viewable within the project, however they can be exported to the client mounted storage, see [Exporting a Dataset](https://docs.rhinohealth.com/hc/en-us/articles/12384845925789-Exporting-a-Dataset).

In the next tutorial we will show you how to analyze the models performance using the Rhino SDK to interact with datasets that exist in a project.


## Auto-Containers

To utilize Rhino FCP's **auto-container** feature, follow these steps:

- Navigate to the Code page in your project
- Select "Create New Code Object"
- Code Object Type: NVIDIA Flare
- NVFLARE Version: 2.6
- Use "New container image"
- Python: 3.11
- Select "browse files"
  - Navigate to the `RhinoFCP/` directory, select `src/infer.py` and `meta.json`, and add these files
- Select "+ Add more" and then "browse folders"
  - Navigate to the `RhinoFCP/` directory, select the `app/` directory and add this folder
- Select UPLOAD FILES
- Under "Requirements" select UPLOAD FILE
  - Navigate to the `RhinoFCP/` directory, select `requirements.txt` and add this file
- Leave the rest of the configurations as the default configurations (i.e No need to set a schema type)
- Select CREATE NEW CODE OBJECT

## Best Practices
* While the auto-container feature is convenient, it lacks the layer caching features of Docker and any time a new version is created it must build the entire image from scratch. Becoming comfortable with Docker can greatly speed up image generation.
* While it may seem faster to move from local training directly to federated training on the platform, setting up the simulation provides an efficient way to work through bugs during developement which would otherwise require time to create the containerized versions, upload to the RhinoFCP, and test there. When done with the RhinoFCP in mind, the files developed during simulation should require minimal changes to transition to production use.

## Other Notes
* Inference can be run on platform post training as well. 
  * Navigate to the Code Runs tab of the project
  * Find the NVFlare training run that contains the global model weights you would like to use for inference
  * Select the **&#8942;** icon on the right side of the code run
  * Select <>Run inference (if this option does not appear, you may be selecting an inference run. Ensure the Type column of the code run you are selecting says **T**)
  * VALIDATION DATASETS: Select the dataset you would like to run inference on
  * MODEL PARAMETERS FILE: If multiple weights files were saved to `/output/model_parameters/`, you may select a specific one here.   
  * Select RUN INFERENCE

## Next Steps
Once complete, proceed to the next portion of the tutorial under `fed_metrics/`.
 