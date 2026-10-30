# Federated Metrics with the Rhino SDK

## Goal
In this section, we show the user some of the tools available to interact with data living within a project on the Rhino FCP. The user will learn how to conduct statistical analysis on decentralized datasets with pre-built python functions. In this tutorial, the user will analyze the AUC performance of each model trained throughout this tutorial to visualize the impact federated learning has on real world data. Furthermore, the user will upload this visualization to the project within the Rhino FCP, enabling collaborators to also view the results.

## Content
A notebook has been prepared to walk the user through an introduction to the Rhino SDK, `notebooks/metrics.ipynb`. Instructions for this portion the tutorial can be found directly embedded within the notebook.

## Before You Start
* `Deploying_Federated_Learning/results/` must contain the 5 prediction files from Parts 1–2: `local_site-1_preds.csv`, `local_site-2_preds.csv`, `local_site-3_preds.csv`, `local_centralized_preds.csv`, `local_simulation_preds.csv`.
* The notebook reads every file in that folder. On Mac, remove any hidden `.DS_Store` file first (`ls -a` to check).

## Expected Results
The ROC plot should show the federated model (AUC ≈ 0.78) close to the simulated model (≈ 0.78), and both above centralized (≈ 0.77) and every single site (best ≈ 0.76).

## Next Steps
You have now completed the Introduction to Federated Learning and the Rhino FCP Tutorial! You should now be able to run these workflows with your own data and models to enable real-world collaboration in production.