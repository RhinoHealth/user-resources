# Rhino FCP Examples - Rhino SDK
This folder contains examples for interacting with Rhino's Federated Computing Platform (FCP) using the Python SDK

# Table of Contents
- [federated-join](./federated-join/Federated_Join_Notebook.ipynb) - Demonstrate the Rhino FCP concept of a federated join, where datasets across sites can be treated as a single, local dataset
- [streamlit-visualization](./streamlit-visualization/README.md) - An example showing the capabilities of combining the Rhino SDK with an interactive application tool such as streamlit
- [xgboost-horizontal](./xgboost-horizontal/README.md) - End-to-end guide for horizontal federated learning with XGBoost (bagged tree-based collaboration) using NVFlare 2.4's Client API on FCP
- [aggregate_quantile_example.ipynb](./aggregate_quantile_example.ipynb) - Demonstrate the Rhino SDK's ability to calculate federated percentiles with differential privacy
- [cox_and_kaplanMeier.ipynb](./cox_and_kaplanMeier.ipynb) - Demonstrate Cox proportional hazard and Kaplan-Meier analysis with federated data
- [eda.ipynb](./eda.ipynb) - Demonstrate usage of the Rhino Python SDK for performing Exploratory Data Analysis (EDA) using federated analytics
- [fhir-pipeline.py](./fhir-pipeline.py) - Demonstrate an end-to-end pipeline for transforming tabular data into FHIR resources and importing it into FCP via the SQL query and Data Harmonization SDK endpoints
- [metrics_examples.ipynb](./metrics_examples.ipynb) - Examples of calculating metrics using federated analytics, including mean, odds ratio, chi square test, t-test, one way anova, and 2x2 matrix
- [pneumonia-results-analysis.ipynb](./pneumonia-results-analysis.ipynb) - Demonstrate usage of the Rhino Python SDK for analyzing code runs using federated analytics
- [runtime_external_files.ipynb](./runtime_external_files.ipynb) - Demonstrate how to make files from a workgroup's S3 bucket available to a Code Run at runtime
- [sql-data-ingestion.ipynb](./sql-data-ingestion.ipynb) - Demonstrate how to get aggregate info or import datasets from queries run on SQL databases that are located on-prem
- [train-test-split.ipynb](./train-test-split.ipynb) - Demonstrate running multi-dataset Generalized Compute with the Rhino Python SDK
- [upsert-objects.ipynb](./upsert-objects.ipynb) - Demonstrate creation and updating of different objects with the Rhino Python SDK

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).

