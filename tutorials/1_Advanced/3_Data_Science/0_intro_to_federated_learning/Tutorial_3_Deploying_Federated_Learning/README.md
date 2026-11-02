# Deploying Federated Learning - Federated DeepChem Tutorial
> Last validated: 2026-10-26

After going through the Intro to Federated Learning and NVFlare Simulation tutorials, this tutorial gives you the opportunity to put everything together in a realistic drug discovery scenario working directly with the Rhino FCP.

## Prerequisites
* Completed `Tutorial_1_Introduction_to_FL` and `Tutorial_2_NVFlare_Simulation`
* The `intro_to_federated_learning` virtual environment (see the parent README)
* For Parts 3 and 4:
  * An active Rhino FCP account with access to create projects
  * Docker and access to your workgroup's ECR, **or** use Auto-Containers (no Docker needed)

## Problem Statement
Pharma and biotech teams often want to collaborate on training predictive models (e.g., binding / activity / inhibition classifiers) without pooling sensitive molecular datasets in a single place. Even when molecules are “SMILES,” the associated labels, assay protocols, and proprietary compound libraries are highly sensitive. Centralizing them can be legally difficult and operationally risky.

We use DeepChem to frame the drug discovery modeling workflow (datasets, featurization, and common training patterns). If you’re new to DeepChem model building or drug discovery, 
this tutorial is a helpful reference, and contains examples of model training and inference using [DeepChem](https://deepchem.io/tutorials/creating-models-with-tensorflow-and-pytorch/).

## Centralized vs. Simulated vs. Federated
This tutorial trains the same model in three ways and compares the results:

| Approach | Where the data is | How the model is trained |
|---|---|---|
| Centralized | All sites' data pooled in one place | One model on all data (baseline; usually not possible with sensitive data) |
| Simulated FL | Split by site, all on your machine | FedAvg across sites as local processes (for development and debugging) |
| Federated (Rhino FCP) | Stays at each site | FedAvg across real FL clients on the platform (production) |

## Resources
- `data/BACE/` - BACE-1 inhibition dataset, laid out to mimic the Rhino FCP file system. Each row is a molecule: 1024 fingerprint features (`X1`–`X1024`), a binary label (`y`) and its SMILES string (`ids`)
  - `site-1/dataset/dataset.csv`, `site-2/dataset/dataset.csv`, `site-3/dataset/dataset.csv` - Training data for each site
  - `centralized/` - The same three site datasets, used together for centralized training
  - `test_df.csv` - Held-out test set used for inference and model comparison
- `local/` - Part 1: local training. See `local/README.md`
  - `src/`
    - `config.py` - Paths, column names and the `SITE` setting (`site-1`, `site-2`, `site-3` or `centralized`)
    - `deepchem_local_train.py` - Trains a DeepChem classifier on one site's data, or on all data combined
    - `infer.py` - Runs inference on `test_df.csv` with a saved local model
- `nvflare_simulation/` - Part 2: NVFlare simulation. See `nvflare_simulation/README.md`
  - `src/` - Exercise files; sections marked with `"""` are left for you to complete
    - `config.py` - Paths and the per-site data loader for simulated clients
    - `create_sim_fed_job.py` - Builds, exports and runs the NVFlare simulation job
    - `deepchem_simulation_train.py` - Client training script using the NVFlare Client API
    - `infer.py` - Runs inference on `test_df.csv` with the simulated global model
  - `solution/` - Completed versions of `create_sim_fed_job.py` and `deepchem_simulation_train.py`
- `RhinoFCP/` - Part 3: deploying to the Rhino FCP. See `RhinoFCP/README.md`
  - `app/` - NVFlare job folder, deployed to every site per `meta.json`'s `deploy_map`
    - `config/`
      - `config_fed_client.json` - Federated client config; points to the training script inside the container
      - `config_fed_server.json` - Federated server config (FedAvg, 30 rounds); saves the global model to `/output/model_parameters.pt`
    - `custom/`
      - `config.py` - Container paths and column names (`/input/datasets/`)
      - `deepchem_fl_train.py` - Client training script for the Rhino FCP
  - `src/`
    - `infer.py` - Inference script the Rhino FCP runs automatically after training, using the global model
  - `Dockerfile` - Builds the container image for the Rhino FCP
  - `docker-push.sh` - Builds the image and pushes it to your workgroup's container registry
  - `meta.json` - NVFlare job metadata (`deploy_map`, `min_clients`)
  - `requirements.txt` - Python dependencies installed in the container
- `fed_metrics/` - Part 4: federated metrics. See `fed_metrics/README.md`
  - `notebooks/`
    - `metrics.ipynb` - Uses the Rhino SDK to compute ROC/AUC on the federated model's predictions, compares all models and posts the plot as a report to the Rhino FCP
- `README.md` - This file

Running Parts 1–2 creates `local/saved_models/`, `nvflare_simulation/saved_models/`, `nvflare_simulation/simulation/` and `results/`. These are generated and not committed.

## Tutorial Contents
Complete the four parts in order. Each one builds on the previous.

| Part | What you do | Runs from | Output | Instructions |
|---|---|---|---|---|
| 1. Local Training | Train a baseline BACE-1 inhibitor classifier on each site's data separately, then on all data combined (centralized) | Terminal (Python scripts) | `local/saved_models/`, `results/local_<site>_preds.csv` | `local/README.md` |
| 2. NVFlare Simulation | Run 3 simulated sites on your machine to validate the FL logic end to end | Terminal (Python scripts) | `nvflare_simulation/saved_models/`, `results/local_simulation_preds.csv` | `nvflare_simulation/README.md` |
| 3. Rhino FCP | Deploy the training container and configs to the Rhino FCP and run true federated training | Rhino FCP UI (+ Docker, or Auto-Containers) | Training (T) and Validation (V) code runs | `RhinoFCP/README.md` |
| 4. Federated Metrics | Use the Rhino SDK to compare single-site, centralized, simulated and federated model performance | Jupyter notebook | ROC plot posted as a report on the V code run | `fed_metrics/README.md` |

## Dataset File Structure
We have organized the file structure in the `data/` directory to mimic the file system encountered when using the Rhino FCP. This way the dataloader between all three training scripts (local, simulation, and Rhino FCP) can remain consistent through this tutorial.

## Getting Help

For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

