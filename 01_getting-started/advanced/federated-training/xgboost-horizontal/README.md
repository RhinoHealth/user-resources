# XGBoost with NVFlare 2.4 Client API - End to End Guide

In this guide, we provide instructions and examples for how to perform horizontal federated learning using XGBoost with bagged tree-based collaboration ([see here](https://github.com/NVIDIA/NVFlare/blob/2.4/examples/advanced/xgboost/tree-based/README.md)) and the NVFlare 2.4 Client API on the Rhino FCP.

In this directory, you will find a number of items:
- `data/` - a directory containing sample data for this guide (see [Preparing the data](#preparing-the-data))
- `xgboost_local/` - a directory containing example code for training an XGBoost mode locally on a single dataset (see [Developing local code](#developing-local-code))
- `output/` - a directory for placing results
- `xgboost_flare/` - a directory containing example code, configs, and other files for training an XGBoost on federated data using the Rhino FCP (see [Federating the training code](#federating-the-training-code))
- `plots.ipynb` - a jupyter notebook containing example code for analyzing the results of the experiment (see [Analyzing results](#analyzing-results))

In the following sections, we will outline how each of these components were constructed and highlight where you can make adjustments based on your specific use case. Before you get started, you may need to install dependencies:

```bash
pip install -r xgboost_flare/requirements.txt
```

## Preparing the data

For this example, we used data from a [Kaggle Credit Risk Dataset](https://www.kaggle.com/datasets/laotse/credit-risk-dataset/data) to simulate a federated learning scenario. 

In particular, we created two small random samples from the dataset: `centralized.csv` (which represents all of the training data) and `test.csv` (which is held out for model evaluation later). We then further broke the "centralized" data into two smaller datasets: `A.csv` and `B.csv`. Ultimately, we will compare the results of training local models on each of `centralized.csv`, `A.csv`, and `B.csv` to training a federated model on both of `A.csv` and `B.csv` using the Rhino FCP.

To reproduce the datasets yourself, download the data from Kaggle (see above), modify the filepaths in `data/scripts/sample.py` as needed, and run the following:

```bash
cd data/scripts
python sample.py
```

To reproduce the federated experiment highlighted in this guide, you will need to import `A.csv` and `B.csv` to your project in the Rhino FCP. To do so, first load the files onto the client ([docs](https://docs.rhinohealth.com/hc/en-us/articles/11386174986397-How-can-I-import-data-in-my-local-environment-onto-my-Rhino-Health-client-using-SFTP)) and then create a dataset in your project ([docs](https://docs.rhinohealth.com/hc/en-us/articles/12385893636509-Creating-a-New-Dataset-or-Dataset-Version)). In "real life", different collaborators possess the different data splits (i.e., `A.csv` and `B.csv` in this case), but no one has access to a the centralized dataset due data sharing limitations.

## Developing local code

Before performing federated training, we developed simple scripts to (a) train and save an XGBoost model locally and (b) make predictions locally using a saved XGBoost model. Our example scripts, which are based on the [XGBoost Tutorials](https://xgboost.readthedocs.io/en/stable/python/python_intro.html#) can be found in `xgboost_local/`.

### Local configurations

For both training and inference scripts, there are some common elements the code needs to reference:
- Paths for reading/writing data, models, and predictions
- Column names for categorical features, numerical features, and labels
- Other constants related to the model structure or training

For convenience, we've stored these in `xgboost_local/config.py` as constants that can be imported in the training and inference scripts. Modify the constants here as needed for your dataset if not using the pre-provided data. 

### Training

Our training script example is in `xgboost_local/train.py` and can be run locally by updating the `prefix` variable in `xgboost_local/config.py` (valid values are "centralized", "A", and "B") and running:

```bash
cd xgboost_local
python train.py
```

The script itself is composed of two major components.

The first is a few line of codes to prepare the data by casting categorical variables to the appropriate type before defining the XGBoost `DMatrix`: 

```python
df_train = pd.read_csv(TRAIN_DATA_PATH)
numeric = df_train[NUMERIC_COLS].astype("float")
categorical = df_train[CATEGORICAL_COLS].astype("category")
labels = df_train[LABEL_COL].astype("int")
dtrain = xgb.DMatrix(
    pd.concat([numeric, categorical], axis=1),
    label=labels,
    enable_categorical=True,
)
```

Note that the code references `config.py` where filepaths, column names, and the number of training rounds have been defined (and imported to `train.py`). In your application, you may want to modify the configuration or pre-processing steps themselves to be suited to your particular dataset.

The second is a few lines of code to train and save the XGBoost model:

```python
xgb_params = {"objective": "binary:logistic"}
model = xgb.train(xgb_params, dtrain, NUM_ROUNDS, evals=[(dtrain, "train")])
model.save_model(MODEL_PATH)
```

Note that for the purposes of this example, we've done the bare minimum to define a binary classifier by setting the `objective` to `binary:logistic`, leaving all other parameters as default, and omitting any evaluation set splitting. In your application, you may want to explore a range of parameters and data splits. See the [XGBoost Documentation](https://xgboost.readthedocs.io/en/stable/) for more.

### Inference

Our inference script is in `xgboost_local/infer.py` and can be run locally after running the [training script](#training) by updating the `prefix` variable in `xgboost_local/config.py` (valid values are "centralized", "A", and "B") and running:

```bash
cd xgboost_local
python infer.py
```

The script itself is composed of 3 components.

The first is a few lines of code to read the test data, which is essentially the same as in the [training script](#training), except reading `test.csv` instead of the file used for training.

The second is a couple of lines of code to read the model from a file and instantiate it:

```python
model = xgb.Booster()
model.load_model(MODEL_PATH)
```

The third is a few lines of code to create the predictions and save them to a file:

```python
scores = model.predict(dtest)
df_test["scores"] = scores
df_test.to_csv(PREDICTION_PATH)
```

## Federating training code

After developing some local code, we can adapt the model to a federated setting on the Rhino FCP. You can see our federated XGBoost example in `xgboost_flare/` (based on [NVFlare's example](https://github.com/NVIDIA/NVFlare/blob/2.4/examples/hello-world/step-by-step/higgs/xgboost)). Please note that the directory structure for the NVFlare job is standardized and follows the latest [NVFlare 2.4 job format convention](https://nvflare.readthedocs.io/en/2.4.0/whats_new.html).

In this example, we perform Horizontal FL with XGBoost using bagged tree-based collaboration. Breaking this down, this means:
- Horizontal FL: each collaborating site is assumed to have the same features, but different data samples 
- XGBoost: the "core" model that we are federating
- Tree-based collaboration: for each round of boosting, trees are trained at every site and aggregated in some way (as opposed to data being represented as a histogram and aggregated before training a model centrally)
- Bagged collaboration: trees from each site are averaged together at each round of boosting (as opposed to cyclic collaboration, in which sites take turns performing a round of boosting and adding their tree to the global model)

### Federating the training code

First, we adapted the training script itself. See the modified script at `xgboost_flare/app/custom/xgboost_fl.py`. The script itself is commented with NVFlare-specific changes. Key changes are summarized below:
1. Import the NVFlare Client API
    ```python
    # (1) import nvflare client API
    from nvflare import client as flare
    ```
2. Initialize the NVFLare Client
    ```python
    # (2) initializes NVFlare client API
    flare.init()
    ```
3. Set up receiving the FLModel from NVFlare
    ```python
    while flare.is_running():
        # (3) receives FLModel from NVFlare
        input_model = flare.receive()
        global_params = input_model.params
        curr_round = input_model.current_round
    ```
4. Placed our local training code in the first round of training
    ```python
    if curr_round == 0:
        # (4) first round, no global model
        model = xgb.train(xgb_params, dtrain, NUM_ROUNDS, evals=[(dtrain, "train")])
        config = model.save_config()
    ```
5. Added code to load the global FL model for subsequent rounds of training
    ```python
    # (5) update model based on global updates
    model_updates = global_params["model_data"]
    for update in model_updates:
        global_model_as_dict = update_model(
            global_model_as_dict, json.loads(update)
        )
    loadable_model = bytearray(json.dumps(global_model_as_dict), "utf-8")
    # load model
    model.load_model(loadable_model)
    model.load_config(config)
    ```

6. Added code to perform the additional round of training on the received global FL model. Note that this makes use of the XGBoost `update` function - which is not part of typical use of the package on local datasets
    ```python
    # (6) train model in two steps
    # first, eval on train and test
    eval_results = model.eval_set(
        evals=[(dtrain, "train")], iteration=model.num_boosted_rounds() - 1
    )
    print(eval_results)
    # second, train for one round
    model.update(dtrain, model.num_boosted_rounds())
    ```
7. Added code to construct the model by taking the tree from the most recent round of boosting
    ```python
    # (7) construct trained FL model
    # Extract newly added tree using xgboost_bagging slicing api
    bst_new = model[model.num_boosted_rounds() - 1 : model.num_boosted_rounds()]
    local_model_update = bst_new.save_raw("json")
    params = {"model_data": local_model_update}
    metrics = {"accuracy": acc}

    output_model = flare.FLModel(params=params, metrics=metrics)
    ```
8. Added code to send the model back to the FL server ([link](./xgboost_flare/app/custom/xgboost_fl.py#L82))
    ```python
    # (8) send model back to NVFlare
    flare.send(output_model)
    ```
9. We also adapted the "local" config file. See the modified file at `xgboost_flare/app/custom/fl_config.py`. In this file, we made two key changes:
    - We removed the filepath constants and added them to the individual training and inference scripts. We've also updated the filepaths to locations in the `/input/` and `/output/` directories - which is where datasets are accessed when running code on the Rhino FCP. See our [tutorial](https://docs.rhinohealth.com/hc/en-us/articles/8088478664349-Tutorial-1-Rhino-Health-Federated-Computing-Platform-Hello-World-Basic-Usage) for explanation of filepaths on the Rhino FCP.
    - Set `NUM_ROUNDS` to 1 - in federated XGBoost we do one round of boosting at a time.


### Creating NVFlare configs

To actually run the [modified training code](#modifying-the-training-code), we need to also define NVFlare job configuration files. For this use case, we used NVFlare's [XGBoost templates](https://github.com/NVIDIA/NVFlare/tree/2.4/job_templates/xgboost_tree).

We made a number of changes to make the template compatible with our code and the Rhino FCP:
- In `config_fed_client.conf` - we updated the `app_script` variable to be `xgboost_fl.py`, the name of our modified training script
- In `config_fed_client.conf` - to remove the pytorch dependency, we changed the path for the `ClientAPILauncherExecutor`:

    ```python
    # old 
    path = "nvflare.app_opt.pt.client_api_launcher_executor.ClientAPILauncherExecutor"

    #new
    path = "nvflare.app_common.executors.client_api_launcher_executor.ClientAPILauncherExecutor"
    ```
- In `config_fed_client.conf` - we updated the `SubProcessLauncher` script to call the appropriate paths on the Rhino FCP:

    ```python
    # old 
    script = "python3 -u custom/{app_script}  {app_config} "

    #new
    script = "python3 /home/localuser/app/custom/{app_script} {app_config} "
    ```
- In `config_fed_server.conf` - we updated `min_clients` from 3 to 2 (we will run the experiment with two sites, corresponding to datasets `A.csv` and `B.csv`)
- In `config_fed_server.conf` - we updated the output file name for the `XGBModelPersistor` so that the Rhino FCP can recognize the final, federated model:

    ```python
    # old 
    save_name = "xgboost_model.json"

    #new
    save_name = "/output/model_parameters.json"
    ```

### Creating the Dockerfile

To create the Dockerfile, we highly recommend using an existing example from our [user resources](./xgboost_flare/Dockerfile) and modifying the last few lines as needed. 

In this case, the entire Dockerfile is boilerplate, except for the two lines that copy in our NVFlare job to the container:

```Docker
COPY --chown=$UID:$GID ./app ./app/
COPY --chown=$UID:$GID ./meta.conf ./infer.py ./
```

You can also avoid creating your own Dockerfile by using Rhino's auto-container functionality. To do this:
- Navigate to the `Code` page in your project
- Select "Create New Code Object"
- Select "NVIDIA Flare" as the type
- Select NVFlare Version 2.4
- Select "New container image"
- Choose your python/CUDA versions
- Upload your `app/` folder (make sure you select "browse folders" to do so), `meta.conf` file, and `infer.py` file
- Enter your requirements and click "create new code object"

### Running model training on Rhino

Once the code, configurations, and Dockerfile are ready - you can push the code to the same project where you imported `A.csv` and `B.csv`. See our [documentation](https://docs.rhinohealth.com/hc/en-us/articles/12385603287325-Pushing-Containers-to-the-ECR) for instructions.

You can then create an NVFlare code object ([docs](https://docs.rhinohealth.com/hc/en-us/articles/12522224013085-Creating-New-NVFlare-Code-or-Code-Version)) and run it on the two datasets you imported ([docs](https://docs.rhinohealth.com/hc/en-us/articles/12522228144669-Running-NVFlare-Code)).

After the training code has successfully run, you can click the three dots on the right-hand side of the completed code run and click "download model parameters" to retrieve a local copy of the model.

## Analyzing results

### Local

To analyze the results locally, place the downloaded model parameters in `output/` and rename the file to `federated_model.json`. Then, update the `prefix` variable in `xgboost_local/config.py` to `federated`, and run:
``` bash
cd xgboost_local
python infer.py
```
Finally, open `plots.ipynb` and run all cells to see the result. Please note that this assumes that you have run the local training code on `A.csv`, `B.csv`, and `centralized.csv` and that you have not modified the filepaths. 

### In the Rhino FCP

You can also perform inference directly in the Rhino FCP. To do so, include the `infer.py` file in the Docker container. The only differences between this file and the file used for local inference are:
- The constants are read from `fl_config.py` rather than `config.py`
- There is no MODEL_PATH constant, rather it is passed as a command line arg to the script call: `model_path = sys.argv[1]`
