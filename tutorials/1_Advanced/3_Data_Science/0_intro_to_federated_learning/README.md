# Introduction to Federated Learning and the Rhino FCP
> Last validated: 2026-10-26

## Goal
We have prepared a thorough set of guides to help users learn answers to the following questions:
* What is federated learning?
* How is federated learning accomplished?
* How can I implement federated learning today using the Rhino FCP?

## Contents and Instructions
This guide is broken into several sub-sections and should be accomplished in the following order:
* `Tutorial_1_Introduction_to_FL`
* `Tutorial_2_NVFlare_Simulation`
* `Tutorial_3_Deploying_Federated_Learning`

Each of these sections contain their own set of instructions and information which will provide answers to the questions stated above.

## Standard Directory Structure

Each tutorial follows a consistent structure:

```
Tutorial N - Name/
├── README.md              # Tutorial documentation
├── data/                  # Tutorial-specific data (if needed)
├── src/                   # Python source files (if needed)
└── notebooks/             # Jupyter notebooks
    └── <tutorial_notebook>.ipynb
```

### Prerequisites
* Python 3.11
* An environment for jupyter notebooks
* An active user account for the Rhino FCP
  * This is only required for certain portions of `Tutorial 3 - Deploying_Federated_Learning`

### Getting Started
Before starting, we will need to configure our environment to ensure we have the necessary packages. It is recommended you do this in an isolated python virtual environment.
```bash
cd tutorials/1_Advanced/3_Data_Science/0_intro_to_federated_learning
python3.11 -m venv .venv/intro_to_federated_learning
source .venv/intro_to_federated_learning/bin/activate 
# On Windows: .venv\intro_to_federated_learning\Scripts\activate
pip install -r requirements.txt
```
> **Note:** Run `pip install -r requirements.txt` from the `0_intro_to_federated_learning/` folder. That is where `requirements.txt` lives.

#### Note
If you plan on running this notebook with Jupyter Notebook, you must register the venv as a kernel after activating it. Please make sure you select this kernel within Jupyter Notebook.
```bash
python -m ipykernel install --user --name intro_to_federated_learning --display-name "intro_to_federated_learning"
```

Once your environment is set up, proceed to `Tutorial_1_Introduction_to_FL`

## Getting Help

For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).