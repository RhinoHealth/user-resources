# Federated Learning Simulation - DeepChem

## Goal
This portion is left as an exercise for the user. The goal is to solidify the user's understanding of developing federated workflows. All skills required for this portion can be found in `Tutorial 2 - NVFlare_Simulation`. We have also provided the complete solution to this exercise under `nvflare_simulation/solution`.

## Contents
In this directory we have already set up the `src/config.py` and `src/infer.py` scripts. The `src/deepchem_simulation_train.py` and `src/create_sim_fed_job.py` files however are intentionally missing code for the user to define. The areas where users must define code are designated by triple-quoted strings.
```python
'''
'''
```
## Instructions
1. Complete the `src/deepchem_simulation_train.py` and `src/create_sim_fed_job.py` scripts.
2. Run the simulated training:
   ```bash
   cd nvflare_simulation/src
   python create_sim_fed_job.py
   ```
3. Once training is complete run inference:
   ```bash
   python infer.py
   ```

## Outputs
Models will be saved in the `saved_models/` directory.

Inference results will be saved in the `Deploying_Federated_Learning/results` directory.

## Notes on Data Loading
The dataloader has been preconfigured in the `src/config.py` file
```python
# Function to get the site dataset for simulated NVFlare training
def get_site_dataset(site):
    TRAIN_DATA_DIR = Path(f"../../../../data/BACE/{site}")
    return TRAIN_DATA_DIR
```
and is called in the training script with
```python
get_site_dataset(flare.get_site_name())
```
NVFlare will automatically name the clients `site-n` for client `n`, so assigning specific datasets to simulated clients can be easily accomplished by creating the `site-n/` subdirectory in your data directory.

## Next Steps
Once complete, proceed to the next portion of the tutorial under `RhinoFCP/`.