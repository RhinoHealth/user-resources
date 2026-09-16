# Introduction to Data Engineering on the Rhino FCP

## Overview

This guide walks through a realistic, end-to-end **data engineering workflow** on the [Rhino Federated Computing Platform (FCP)](https://dashboard.rhinohealth.com/login).

By the end, you should have a better understanding of:

* How the Rhino FCP is structured (clients, cloud, and the distinction between them)
* (**Tutorial 0**) How to get data onto a Rhino client
* (**Tutorial 1**) How to register datasets and schemas
* (**Tutorial 2**) How to explore data using federated analytics
* (**Tutorial 3**) How to transform & preprocess data through automated scripts
* (**Tutorial 4**) How to harmonize source data to OMOP target tables
* (**Tutorial 5**) How to validate harmonized outputs against OMOP quality standards
* (**Tutorial 6**) How to derive ML-ready features from validated OMOP data
* (**Tutorial 7**) How to select patient cohorts from a feature table
* (**Tutorial 8**) How to accomplish all of the above conversationally using AI via the Rhino MCP

> NOTE: This is not a comprehensive overview of ALL platform capabilities, but it’s a solid starting point to help you get up and running.

---

## Who This Guide Is For

This guide is written for clinical data engineers, research informatics staff, and project coordinators.

**No advanced prior Rhino FCP experience is assumed.** Each tutorial explains the *why* alongside the *how*.

---

## The Rhino FCP

### Overview

[Rhino’s Federated Computing Platform](https://docs.rhinohealth.com/hc/en-us/articles/12508780361373-The-Rhino-Federated-Computing-Platform-FCP) (FCP) is a secure, scalable system that enables organizations to collaborate without moving or centralizing underlying data. It works by sending computation to where data resides—across cloud or on-prem environments—and only sharing aggregated results, preserving data ownership and privacy.

- The platform connects and harmonizes distributed datasets, allowing teams to run analytics, train models, and deploy workflows across multiple participants as if the data were unified.

- FCP includes built-in privacy, security, and governance controls—such as encryption, access controls, and privacy-enhancing technologies—to ensure compliant and trusted collaboration.

- It also provides orchestration, tooling, and MLOps capabilities to manage the full lifecycle of data processing and AI development in a federated environment.

Overall, FCP enables organizations across industries to unlock insights from distributed data networks while maintaining strict control, security, and regulatory compliance.

### Architecture

The Rhino FCP has two distinct parts:

```
Your Site                              Rhino Cloud
┌────────────────────────────┐         ┌─────────────────────────────┐
│  Rhino Client              │         │  Rhino FCP Cloud            │
│  (also called: Rhino Agent,│◄───────►│  (Orchestrator)             │
│   Edge Node)               │         │                             │
│                            │         │  • Project management       │
│  • Data lives here         │         │  • Schema/mapping registry  │
│  • Code runs here          │         │  • Federated analytics      │
│  • Data never leaves       │         │    results aggregation      │
│    the client's network    │         │  • Run monitoring & logs    │
└────────────────────────────┘         └─────────────────────────────┘
```

The **Rhino client** (Rhino agent / edge node) is where your data is securely stored and where all computation happens. Data never leaves the client's network boundary. Only metadata, aggregated results, and run status are sent to the Rhino cloud.

Rhino offers several client hosting options:

| Hosting Model | Description |
|---|---|
| **Self-hosted (on-prem)** | Client deployed on your own hardware within your firewall |
| **Rhino-managed cloud** | Rhino deploys and manages a client on AWS, GCP, or Azure in a dedicated environment |
| **Hybrid** | Some compute on-prem, storage in a managed cloud environment |

Ask your Rhino administrator or account team which model your organization uses. 
> The tutorials in this guide work identically regardless of hosting model.

### Single-Site Workflow

This tutorial walks through the workflow from the perspective of **a single site** — one hospital, clinic, or data partner. You will register data, clean it, and harmonize it as if you are the data engineer with access to a singular client node. This keeps the tutorial focused and runnable without needing additional infrastructure.

### Federated Workflow

In a real multi-site federated project, this same workflow runs across **two or more sites simultaneously**, with a data engineer at each site executing the same steps against their own local data. The key differences are:

- **Each site may register its own datasets.** Files are not shared between sites.
- **Each site runs the same Code Objects** (cleaning scripts) against their own data. The script runs locally; only the output metadata is registered with the FCP.
- **Federated analytics** (Tutorial 2) automatically aggregate results across all sites — you ask one question and get a combined answer without any site seeing another site's raw data.
- **Harmonization mappings** (Tutorial 4) are defined once and can be re-run at every participating site, ensuring all produce outputs with the same structure. Schemas can also be defined at a singular site and shared across multiple datasets at different sites.

```
Site A (Hospital)              Site B (Clinic)             Site C (Research Center)
┌──────────────────┐           ┌──────────────────┐          ┌──────────────────┐
│ patients_a.csv   │           │ patients_b.csv   │          │ patients_c.csv   │
│ encounters_a.csv │           │ encounters_b.csv │          │ encounters_c.csv │
│ procedures_a.csv │           │ procedures_b.csv │          │ procedures_c.csv │
│                  │           │                  │          │                  │
│  Rhino Agent     │           │  Rhino Agent     │          │  Rhino Agent     │
│  (on-prem)       │           │  (on-prem)       │          │  (on-prem)       │
└────────┬─────────┘           └────────┬─────────┘          └────────┬─────────┘
         │                              │                              │
         │   metadata + aggregates only │                              │
         └──────────────────────────────┴──────────────────────────────┘
                                        │
                                        ▼
                              Rhino FCP (Cloud)
                   ┌──────────────────────────────────┐
                   │  Shared project space:           │
                   │  Schemas, Code Objects,          │
                   │  Harmonization Mappings,         │
                   │  Federated Analytics Results     │
                   └──────────────────────────────────┘
                                        ▲
                        Research Coordinator / You
                             (Orchestrator Notebook)
```

> **Raw patient data never leaves any site.** The FCP only ever receives metadata, aggregate statistics, and on-site-generated outputs. Nothing in this workflow uploads patient records to the cloud.

Everything you learn in this single-site tutorial applies directly to the multi-site federated case. The only difference is that in a federated project, each site runs the same steps locally, and the FCP handles aggregation automatically.

---

## Project Directory

```
intro_to_data_engineering/
│
├── README.md                                    # This file
├── requirements.txt                             # Dependencies
│
├── data/                                        # Shared synthetic datasets
│   ├── patients.csv
│   ├── encounters.csv
│   └── procedures.csv
│
├── Tutorial 0 - Getting_Data_Onto_the_Client/
│   └── README.md
│
├── Tutorial 1 - Dataset_Registration/
│   ├── README.md
│   ├── data/                                    # Tutorial-specific data (if any)
│   ├── src/                                     # Python scripts (if any)
│   └── notebooks/
│       └── dataset_registration.ipynb
│
├── Tutorial 2 - Data_Discovery/
│   ├── README.md
│   ├── data/
│   ├── src/
│   └── notebooks/
│       └── data_discovery.ipynb
│
├── Tutorial 3 - Data_Preparation/
│   ├── README.md
│   ├── data/
│   ├── src/
│   └── notebooks/
│       └── data_preparation.ipynb
│
├── Tutorial 4 - Harmonization/
│   ├── README.md
│   ├── data/
│   ├── src/
│   └── notebooks/
│       └── harmonization.ipynb
│
├── Tutorial 5 - Validation/
│   ├── README.md
│   ├── data/
│   ├── src/
│   └── notebooks/
│       └── validation.ipynb
│
├── Tutorial 6 - Feature_Engineering/
│   ├── README.md
│   └── notebooks/
│       └── feature_engineering.ipynb
│
├── Tutorial 7 - Cohort_Selection/
│   ├── README.md
│   ├── cohort_selection_code_snippets.py
│   └── notebooks/
│       └── cohort_selection.ipynb
│
└── Tutorial 8 - Rhino_MCP/
    ├── README.md
    ├── data/
    ├── src/
    └── notebooks/
        └── rhino_mcp.ipynb
```

---

## Example Datasets

Three synthetic clinical datasets are included in the `data/` folder. **All data is fictional.**

| File | Description | Rows | Key Columns |
|------|-------------|------|-------------|
| `data/encounters.csv` | One row per clinical visit | 100 | `patientID`, `visitID`, `DateOfService`, `TypeOfService` |
| `data/patients.csv` | One row per patient | 100 | `patientID`, `YearOfBirth`, `Gender`, `Race`, `Ethnicity` |
| `data/procedures.csv` | One row per procedure | 100 | `patientID`, `visitID`, `ProcedureDate`, `ProcedureDescription`, `ProcedureCode`, `ProcedureCategory` |

> In a real deployment, equivalent files would live on each site's client node and would never be uploaded anywhere.

The datasets intentionally contain issues that will be discovered in Tutorial 2 and resolved in Tutorial 3:

| Issue | Where |
|---|---|
| Casing inconsistencies (`"male"`, `"MALE"`, `"Male"`) | `patients.Gender`, `encounters.TypeOfService` |
| Null / empty values in required fields | `patients.Gender` (rows 23, 76), `encounters.DateOfService` (row 73), `procedures.ProcedureCode` (row 92) |
| Invalid values (`"Alien"` in Gender, `YearOfBirth = 10000`) | `patients` rows 41, 45 |
| Exact duplicate rows | Last row of each CSV is a duplicate of row 3 |

---

## Supported Data Types

The examples in this guide use **CSV (tabular) data**, but the Rhino FCP supports a broader range of data types:

| Data Type | Formats Supported | Notes |
|---|---|---|
| **Tabular** | CSV, Parquet | This tutorial uses CSV |
| **Imaging** | DICOM, jpg, png | Registered as file datasets; no schema required |
| **Other files** | Any binary format | Can be registered as unstructured datasets |


---

## Set Up

### Prerequisites

- Running Rhino Client (& the ability to add sample data if not already present)
- Active Rhino FCP account tied to a Rhino workgroup
- Access to a Rhino Project (or the ability to create one)
  - Identify your `PROJECT_UID` : [instructions](https://docs.rhinohealth.com/hc/en-us/articles/13004015836829-How-do-I-retrieve-a-Project-s-Collaborator-s-Data-Schema-s-Dataset-s-Code-Object-s-or-Code-Run-s-UID)
- Python 3.11+
- Jupyter Notebook, JupyterLab, or VS Code with the Jupyter extension

### Confirm Your Rhino Client Is Running

Before any data work can happen, a **Rhino client** must be deployed and connected to the FCP cloud.

> If your organization already has a running Rhino client and you can log into the FCP Dashboard, skip this step.

Log in to the FCP Dashboard at **[https://dashboard.rhinohealth.com/login](https://dashboard.rhinohealth.com/login)**. 
- Navigate to **Settings** (by clicking the gear icon on the sidebar)
- Confirm your "Organization" and "Primary Workgroup"
- Scroll down to "Your Rhino Client" - a status of "Online" indicates the client agent is connected and healthy

If no "Primary Workgroup" is listed, or the agent shows as disconnected, contact [support@rhinohealth.com](mailto:support@rhinohealth.com) before proceeding.

### Environment Setup

```bash
python3 -m venv .venv/rhino_data_engineering

source .venv/rhino_data_engineering/bin/activate
# Windows: .venv\rhino_data_engineering\Scripts\activate

# Navigate to top-level directory (e.g., cd ~/workspace/solutions/demos/intro_to_data_engineering)
pip install -r requirements.txt
```

### Running Notebooks

**Option A — Jupyter Notebook or JupyterLab (browser-based)**

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

**Option B — VS Code**

1. Install the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) in VS Code
2. Open any `.ipynb` file
3. Click the kernel selector (top-right of the notebook) → **Select Another Kernel** → **Python Environments** → choose the `rhino_data_engineering` venv
4. Run cells with **Shift+Enter** or the ▶ button

**Option C — Terminal (nbconvert)**

To run a notebook non-interactively:
```bash
jupyter nbconvert --to notebook --execute Tutorial_1.ipynb --output Tutorial_1_executed.ipynb
```

---

## Tutorial Sequence

| # | Folder | What You Will Do |
|---|--------|-----------------|
| 0 | `Tutorial 0 - Getting_Data_Onto_the_Client` | Transfer example CSV files to the Rhino client and verify they are accessible |
| 1 | `Tutorial 1 - Dataset_Registration` | Register datasets and generate corresponding Data Schemas |
| 2 | `Tutorial 2 - Data_Discovery` | Explore data with federated analytics |
| 3 | `Tutorial 3 - Data_Preparation` | Clean and standardize with Code Objects |
| 4 | `Tutorial 4 - Harmonization` | Map source data to target OMOP standard using the Rhino DHE |
| 5 | `Tutorial 5 - Validation` | Verify harmonized output meets OMOP quality standards |
| 6 | `Tutorial 6 - Feature_Engineering` | Derive ML-ready patient-level features from validated OMOP data |
| 7 | `Tutorial 7 - Cohort_Selection` | Select targeted patient subsets from the feature table |
| 8 | `Tutorial 8 - Rhino_MCP` | Accomplish all of the above via AI natural language with Claude |

### Components

Each tutorial includes a combination of:

| Item | Purpose |
|---|---|
| **README.md** | Markdown files containing context and instructions |
| **Interactive Python Notebooks** | Jupyter-compatible `.ipynb` files that demonstrate and automate tasks using the Rhino SDK |
| [**Rhino Dashboard**](https://dashboard.rhinohealth.com/login) | Rhino FCP web interface |

Each README includes a **"Checking Your Work in the Dashboard"** section that tells you exactly where to look in the web UI to visually inspect what has been created, monitor running jobs, and troubleshoot issues.

Key sections of the Dashboard include:

| Section | Purpose (within Tutorial) |
|---|---|
| **Projects** | View all your projects and navigate into a specific project |
| **Datasets** | See registered datasets, their row counts, schemas, and status |
| **Data Schemas** | Inspect schema definitions and field types |
| **Code Objects** | View registered scripts and containers |
| **Code Runs** | Monitor running and completed jobs, view logs |
| **Harmonization** | View and manage semantic and syntactic mappings |
| **Workgroups** | Check site connectivity and agent status |

### SDK vs. UI

The Python notebooks demonstrate how to **automate** the workflow using the Rhino Python SDK. Every step can also be performed manually through the FCP Dashboard — no code required.

The notebooks and the UI do the same things. Use whichever fits your workflow:
- **Notebooks** — best for reproducible, version-controlled pipelines and multi-site automation
- **UI** — best for manual exploration, one-off tasks, monitoring, and approving mappings

---

## Helpful Links

| Resource | Description |
|---|---|
| [Rhino FCP Dashboard](https://dashboard.rhinohealth.com/login) | The FCP web UI — where you monitor runs, inspect datasets, and manage mappings |
| [Rhino Documentation](https://docs.rhinohealth.com/hc/en-us) | Full product documentation including tutorials and concept guides |
| [Rhino Python SDK Docs](https://rhinohealth.github.io/rhino_sdk_docs/html/index.html) | SDK reference documentation and quickstart guide |

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
