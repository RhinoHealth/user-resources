# Local Training - DeepChem

## Goal
Before performing federated training, want to ensure our local training script works appropriately. For illustrative purposes of the tutorial,we would also like to observe individual site performance and compare it to federated performance. To get started, we have developed scripts to enable:
1.  Training and saving a Deepchem model locally.
2.  Making predictions locally using saved Deepchem model weights.

## Local Configurations
For both training and inference scripts, there are some common elements the code needs to reference:
1. Data
2. Paths for reading/writing data, models, and predictions
3. Column names for categorical features, numerical features, and labels

For convenience, we've stored these in `src/config.py`. <br>
If using the provided data, the only variable that needs to be changed in `src/config.py` is `SITE` and should be set to `site-1`, `site-2`, `site-3`, or `centralized`.  
 
Using other data may require modifying other constants as needed.

### Data
The BACE (Beta-secretase 1) dataset is a binary classification dataset used to predict whether a molecule will inhibit the BACE-1 enzyme. BACE-1 is a key pharmacological target for Alzheimer's disease; thus, this dataset is fundamental for virtual screening in drug discovery efforts.
This data can be found in the `data/BACE` directory of the project and is split up among multiple sites for federated learning.
1. `site-1/dataset/dataset.csv`
2. `site-2/dataset/dataset.csv`
3. `site-3/dataset/dataset.csv`
4. `test_df.csv`

There is also a `centralized` folder in this directory that contains all three site's data. The local script handles concatenating these datasets natively. 

## Training

Review the provided training script (`src/deepchem_local_train.py`) and once comfortable with its workflow, edit `src/config.py` so that `SITE` is one of the 4 valid values. Then run the training script.
```
cd local/src
python deepchem_local_train.py
```
The script trains a DeepChem model for BACE-1 inhibition binary classification. The resulting model can be found in `saved_models/local_{SITE}.pt` <br>
**Repeat this process for all 4 valid site values.**

## Inference
To obtain predictions on the test set we also provide `src/infer.py`. Similarly to training, the `src/config.py` value for `SITE` must reflect which site's model you would like to perform the inference on.
While the training script also outputs performance metrics, we provide an inference script, `src/infer.py`, <br>
to run inference and save the model output to the path defined in the `src/config.py` file.
```
cd local/src
python infer.py
```
## Outputs

Models will be saved in the `saved_models/` directory.

Inference results will be saved in the `Deploying_Federated_Learning/results` directory.

## Next Steps
Once complete, proceed to the next portion of the tutorial under `nvflare_simulation/`.