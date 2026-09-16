# Deploying Federated Learning - Federated DeepChem Tutorial 

After going through the Intro to Federated Learning and NVFlare Simulation tutorials, this tutorial gives you the opportunity to put everything together in a realistic drug discovery scenario working directly with the Rhino FCP.

## Problem Statement
Pharma and biotech teams often want to collaborate on training predictive models (e.g., binding / activity / inhibition classifiers) without pooling sensitive molecular datasets in a single place. Even when molecules are “SMILES,” the associated labels, assay protocols, and proprietary compound libraries are highly sensitive. Centralizing them can be legally difficult and operationally risky.

We use DeepChem to frame the drug discovery modeling workflow (datasets, featurization, and common training patterns). If you’re new to DeepChem model building or drug discovery, 
this tutorial is a helpful reference, and contains examples of model training and inference using [DeepChem](https://deepchem.io/tutorials/creating-models-with-tensorflow-and-pytorch/).

## Tutorial Contents
This tutorial is split into four parts shows a realistic workflow for privacy-preserving collaboration in drug discovery. The modules build off of each other so they should be completed in the following order:

1. Local Training: train a baseline BACE-1 inhibitor classifier on one site’s data.
   1. See `local/README.md` for more detail.

2. Federated Learning NVFlare Simulation: run multiple “sites” on your laptop/workstation to validate the FL logic end-to-end.
   1. See `nvflare_simulation/README.md` for more detail.

3. Federated Learning on the Rhino FCP: Deploy federated training container and configurations to Rhino’s Federated Compute Platform, enabling true federated training.
   1. See `RhinoFCP/README.md` for more detail.

4. Federated Metrics with Rhino SDK: Use the Rhino SDK to extract federated metrics and compare single site, centralized, simulated and non-simulated federated models performance.
   1. See `fed_metrics/README.md`.

## Dataset File Structure
We have organized the file structure in the `data/` directory to mimic the file system encountered when using the Rhino FCP. This way the dataloader between all three training scripts (local, simulation, and Rhino FCP) can remain consistent through this tutorial.

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](support@rhinohealth.com)

