# Introduction to Data Engineering
> Last validated: 2026-11-04

# Overview

This foundational tutorial series walks through a realistic, end-to-end **data engineering workflow** on the [Rhino Federated Computing Platform](https://docs.rhinofcp.com/introduction-to-the-rhino-federated-computing-platform-fcp/the-rhino-federated-computing-platform-fcp) (FCP).

**No advanced prior Rhino FCP experience is assumed.** 

Each tutorial feeds into the next, so we highly recommend completing all steps in order. See [Resources](#resources) below for what each tutorial covers.

By the end, you should have a better understanding of how the Rhino FCP is structured (Rhino clients, Rhino orchestrator, and the distinction between them), and of the full data engineering lifecycle it supports - from getting raw data onto a client through to ML-ready patient cohorts.

> NOTE: This is not a comprehensive overview of ALL platform capabilities, but it’s a solid starting point to help you get up and running.


# The Rhino FCP

## Overview

[Rhino’s Federated Computing Platform](https://docs.rhinofcp.com/introduction-to-the-rhino-federated-computing-platform-fcp/the-rhino-federated-computing-platform-fcp) (FCP) is a secure, scalable system that enables organizations to collaborate without moving or centralizing underlying data. It works by sending computation to where data resides—across clouds and/or on-prem environments—and only sharing aggregated results, preserving data ownership and privacy.

- The platform connects and harmonizes distributed datasets, allowing teams to run analytics, train models, and deploy workflows across multiple participants as if the data were unified.

- FCP includes built-in privacy, security, and governance controls—such as encryption, access controls, and privacy-enhancing technologies—to ensure compliant and trusted collaboration.

- It also provides orchestration, tooling, and MLOps capabilities to manage the full lifecycle of data processing and AI development in a federated environment.

Overall, FCP enables organizations across industries to unlock insights from distributed data networks while maintaining strict control, security, and regulatory compliance.

## Architecture

The Rhino FCP has two distinct components:

```
The Rhino Client                   The Rhino Orchestrator
┌────────────────────────────┐     ┌──────────────────────────────────────┐
│ aka. Rhino Agent,          │◄───►│ aka. Rhino Cloud, central aggregator │
│      edge node / VM        │     │                                      │
│                            │     │  • Project & permissions management  │
│  • Data lives here         │     │  • Dataset, schema, mapping registry │
│  • Code runs here          │     │  • Federated analytics &             │
│  • Data never leaves       │     │    results aggregation               │
│    the client's network    │     │  • Run monitoring & logs             │
└────────────────────────────┘     └──────────────────────────────────────┘
```

The **Rhino client** is where your data is securely stored and where all computation happens. Data never leaves the client's network boundary. Only metadata, aggregated results, and run status are sent to the central **Rhino orchestrator**.

Rhino offers several client hosting options:

| Hosting Model | Description |
|---|---|
| **Self-hosted (on-prem)** | Client deployed on your own hardware within your firewall |
| **Self-hosted (on cloud)** | Client deployed on cloud environment (e.g., AWS, GCP, Azure) |
| **Rhino-managed** | Rhino deploys and manages client on behalf of customer |
| **Hybrid** | E.g., Compute on-prem, storage in a managed cloud environment |

> The tutorials in this guide work identically regardless of hosting model.

## Single-Site Workflow

This tutorial walks through the workflow from the perspective of **a single site** — one hospital, clinic, or research center. You will register data, clean it, and harmonize it as if you are the data engineer with access to a singular client node. This keeps the tutorial focused and runnable without needing additional infrastructure.

## Federated Workflow

In a typical multi-site federated project, this same workflow runs across **two or more sites simultaneously**, with a data engineer at each site executing the same steps against their own local data. The key differences are:

- **Each site may register its own datasets.** Datasets are not shared between sites and will reside in separated silos. For this example, we assume that the dataset input schemas are already aligned across sites, but this is often not the case in real-world scenarios.
- **Each site runs any necessary Code Objects** (cleaning scripts) against their own data. Scripts run locally on each Rhino Client; only output metadata is registered with the FCP.
- **Federated analytics** automatically aggregate results across all sites — you ask one question and get a combined answer without any site seeing another site's raw data.
- **Harmonization mappings** are defined once and can be re-run at every participating site (assuming target datasets have the same input and output schemas). Schemas can also be defined at a singular site and shared across multiple datasets at different sites.

Example Federated Network:

```
Site A (Hospital)              Site B (Clinic)             Site C (Research Center)
┌──────────────────┐           ┌──────────────────┐          ┌──────────────────┐
│ patients_a.csv   │           │ patients_b.csv   │          │ patients_c.csv   │
│ encounters_a.csv │           │ encounters_b.csv │          │ encounters_c.csv │
│ procedures_a.csv │           │ procedures_b.csv │          │ procedures_c.csv │
│                  │           │                  │          │                  │
│  Rhino Client    │           │  Rhino Client    │          │  Rhino Client    │
│  (on-prem)       │           │  (AWS)           │          │  (GCP)           │
└────────┬─────────┘           └────────┬─────────┘          └─────────┬────────┘
         │                              │                              │
         │   metadata + aggregates only │                              │
         └──────────────────────────────┴──────────────────────────────┘
                                        │
                                        ▼
                    Rhino FCP Orchestrator (Rhino Cloud)
                   ┌──────────────────────────────────┐
                   │  Shared project space:           │
                   │  Permissions Policy,             │
                   │  Schemas, Code Objects,          │
                   │  Harmonization Mappings,         │
                   │  Federated Analytics Results     │
                   └──────────────────────────────────┘
                                        ▲
                                  Data Engineer
                        (Interact via FCP Dashboard UI, SDK, or MCP)
```

> **Raw patient data never leaves any site.** The orchestrator only ever receives metadata, aggregate statistics, and on-site-generated outputs.

Everything you learn in this single-site tutorial applies directly to the multi-site federated case. The only difference is that in a federated project, each client site runs the same steps locally, and the FCP orchestrator handles aggregation automatically.

# Resources
- [`data/`](./data/) - Shared synthetic datasets used across the tutorials (see [Dataset Info](#dataset-info) below)
  - [`encounters.csv`](./data/encounters.csv) - tabular data representing patient visits
  - [`patients.csv`](./data/patients.csv) - tabular data representing patient demographics
  - [`procedures.csv`](./data/procedures.csv) - tabular data representing patient procedures
- [`Tutorial_0_Getting_Data_Onto_the_Client/`](./Tutorial_0_Getting_Data_Onto_the_Client/) - Transfer the example CSV files onto the Rhino Client and verify they're accessible
- [`Tutorial_1_Dataset_Registration/`](./Tutorial_1_Dataset_Registration/) - Register the datasets and generate their corresponding Data Schemas
- [`Tutorial_2_Data_Discovery/`](./Tutorial_2_Data_Discovery/) - Explore the data using Federated (aggregate-only) Analytics
- [`Tutorial_3_Data_Preparation/`](./Tutorial_3_Data_Preparation/) - Clean and standardize the data using Code Objects
- [`Tutorial_4_Harmonization/`](./Tutorial_4_Harmonization/) - Map the source data to the OMOP target standard using the Rhino Data Harmonization Engine (RhinoDHE)
- [`Tutorial_5_Validation/`](./Tutorial_5_Validation/) - Verify the harmonized output meets OMOP quality standards
- [`Tutorial_6_Feature_Engineering/`](./Tutorial_6_Feature_Engineering/) - Derive ML-ready, patient-level features from the validated OMOP data
- [`Tutorial_7_Cohort_Selection/`](./Tutorial_7_Cohort_Selection/) - Select targeted patient subsets from the feature table
- [`Tutorial_8_Rhino_MCP/`](./Tutorial_8_Rhino_MCP/) - Accomplish all of the above conversationally, via natural language, using the Rhino MCP Server
- [`README.md`](./README.md) - This file
- [`requirements.txt`](./requirements.txt) - Python dependencies for running the tutorial notebooks locally

# Dataset Info

Three synthetic clinical datasets are included in the `data/` folder. **All data is fictional.**

| File | Description | Rows | Key Columns |
|------|-------------|------|-------------|
| `data/encounters.csv` | One row per clinical visit | 100 | `patientID`, `visitID`, `DateOfService`, `TypeOfService` |
| `data/patients.csv` | One row per patient | 100 | `patientID`, `YearOfBirth`, `Gender`, `Race`, `Ethnicity` |
| `data/procedures.csv` | One row per procedure | 100 | `patientID`, `visitID`, `ProcedureDate`, `ProcedureDescription`, `ProcedureCode`, `ProcedureCategory` |

> In a real deployment, equivalent files would live on each site's client node and never move.

The datasets intentionally contain issues that will be discovered in [Tutorial 2](./Tutorial_2_Data_Discovery/) and resolved in [Tutorial 3](./Tutorial_3_Data_Preparation/):

| Issue | Where |
|---|---|
| Casing inconsistencies (`"male"`, `"MALE"`, `"Male"`) | `patients.Gender`, `encounters.TypeOfService` |
| Null / empty values in required fields | `patients.Gender` (rows 23, 76), `encounters.DateOfService` (row 73), `procedures.ProcedureCode` (row 92) |
| Invalid values (`"Alien"` in Gender, `YearOfBirth = 10000`) | `patients` rows 41, 45 |
| Exact duplicate rows | Last row of each CSV is a duplicate of row 3 |

Note: the examples in this guide use **CSV (tabular) data**, but the Rhino FCP supports a broader range of data types:

| Data Type | Formats Supported | Notes |
|---|---|---|
| **Tabular** | CSV, Parquet | This tutorial uses CSV |
| **Imaging** | DICOM, jpg, png | Registered as file datasets; no schema required |
| **Other files** | Any binary format | Can be registered as unstructured datasets |


# Tutorial Info

Each individual tutorial includes a combination of:

| Item | Purpose |
|---|---|
| **README.md** | Markdown files containing context and instructions. **START HERE!** |
| **Interactive Python Notebooks** | Jupyter-compatible `.ipynb` files that demonstrate and automate tasks using the Rhino SDK |
| [**Rhino Dashboard**](https://dashboard.rhinohealth.com/login) | Sections explaining what you can do and where to look in the Rhino FCP web interface |

# Tutorial Instructions

1. Read through this entire [README.md](README.md)
2. Complete the [Getting Started](#getting-started) section below
3. Proceed through the tutorials in order
- The READMEs in each subfolder will walk you through what to do, step-by-step


# Getting Started

## Prerequisites

- FCP Credentials (email and password)
- A Rhino Agent (client / edge node)
- Stable internet connection
- Access to a fresh Rhino Project (or the ability to create one)
  - Identify your `PROJECT_UID` : [instructions](https://docs.rhinofcp.com/creating-and-running-code-objects/finding-and-copying-an-objects-uid)
- Python 3.11+
- Jupyter Notebook, JupyterLab, or VS Code with the Jupyter extension

## Access the FCP Dashboard

Follow these steps:

- [How to Login](https://docs.rhinofcp.com/getting-started/quick-start-guide/logging-in-to-rhino-fcp)
- [How to Reset Your Password](https://docs.rhinofcp.com/getting-started/quick-start-guide/resetting-your-rhino-fcp-password)

If you have not received your credentials, or are having trouble accessing the system, please contact support@rhinofcp.com.

Familiarize yourself with the The [FCP Dashboard UI](https://docs.rhinofcp.com/getting-started/quick-start-guide/the-fcp-dashboard).

## Configure your Environment

To configure your environment, please follow the steps on [this page](https://docs.rhinofcp.com/getting-started/quick-start-guide/fcp-client-installation-and-environment-configuration). 

Verify that your client is online by following [this guide](https://docs.rhinofcp.com/getting-started/quick-start-guide/check-the-status-of-your-fcp-client).

Assuming you are working out of command line (e.g., using an IDE like VSCode), run the following bash commands to set up a virtual environment with the necessary requirements:

```bash
python3 -m venv .venv/rhino_data_engineering

source .venv/rhino_data_engineering/bin/activate
# Windows: .venv\rhino_data_engineering\Scripts\activate

# Navigate to top-level directory (e.g., cd ~/workspace/solutions/demos/intro_to_data_engineering)
pip install -r requirements.txt
```

## Running Notebooks

#### **Option A — Jupyter Notebook or JupyterLab (browser-based)**

Register the virtual environment as a kernel first:
```bash
python -m ipykernel install --user \
  --name rhino_data_engineering \
  --display-name "rhino_data_engineering"
```
Then launch:
```bash
jupyter notebook    # or: jupyter lab
```
Open any `.ipynb` file and select **rhino_data_engineering** from the kernel picker (top-right in Jupyter Notebook, or the kernel selector bar in JupyterLab).

#### **Option B — VS Code**

1. Install the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) in VS Code
2. Open any `.ipynb` file
3. Click the kernel selector (top-right of the notebook) → **Select Another Kernel** → **Python Environments** → choose the `rhino_data_engineering` venv
4. Run cells with **Shift+Enter** or the ▶ button

#### **Option C — Terminal (nbconvert)**

To run a notebook non-interactively:
```bash
jupyter nbconvert --to notebook --execute Tutorial_1.ipynb --output Tutorial_1_executed.ipynb
```

# SDK vs. UI

The Python notebooks demonstrate how to **automate** the workflow using the Rhino Python SDK. Every step can also be performed manually through the FCP Dashboard — no code required.

The notebooks and the UI do the same things. Use whichever fits your workflow:
- **Notebooks** — best for reproducible, version-controlled pipelines and multi-site automation
- **UI** — best for manual exploration, one-off tasks, monitoring, and approving mappings


# Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
