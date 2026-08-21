# Federated Imaging Demo — Rhino SDK Notebook

A guided walkthrough of the Rhino Federated Computing Platform using the BreastMNIST
dataset: register data, run federated analytics, demonstrate built-in privacy
protection (k-anonymization), and train a shared model across simulated sites using
NVIDIA FLARE — all without any site's raw data ever leaving its source.

## Repo contents

```
federated_imaging_demo/
├── sdk.ipynb                          ← the demo notebook (start here)
├── requirements.txt
├── images/
│   └── Rhino logomark.png             ← used in the notebook's banner cells
└── containers/
    ├── ImagePixelExtraction/          ← preprocessing container
    │   ├── image_pixel_extraction.py
    │   └── requirements.txt
    └── NVFlare/                       ← federated training container 
        ├── app/config/config_fed_client.json
        ├── app/config/config_fed_server.json
        ├── app/custom/train.py
        └── requirements.txt
```

---

## The notebook's five phases

`sdk.ipynb` follows the Rhino demo-notebook guidelines' phase structure:

| Phase | Title | What happens |
|---|---|---|
| **1** | Connect | Authenticate to Rhino FCP and create the project |
| **2** | Prepare the Data | Register the BreastMNIST dataset and preprocess it into a simulated two-site split |
| **3** | Explore Data Across Sites | Federated descriptive statistics, significance tests, and a k-anonymization privacy demo — across both sites |
| **4** | Train a Shared Model | Train a shared model across both sites using NVIDIA FLARE, with no raw data pooled |
| **5** | Export the Model | Download the globally trained weights for local inference or further evaluation |

---

## Prerequisites

- Python 3.9+
- A Rhino Health account with access to the target environment 
- Access to the client-mounted data path referenced in the Dataset Creation step
- The `containers/ImagePixelExtraction/` and `containers/NVFlare/` folders, kept at
  their current relative paths — the notebook reads these files directly to build
  the code objects, so renaming or moving them will break the corresponding cell

## Setup

```bash
pip install -r requirements.txt
```

Then open the notebook and run cells top to bottom on first use. `password=getpass()`
prompts for your Rhino account password at runtime — credentials are never hardcoded.


## Variables to configure

Each of these appears at the top of its relevant cell, marked for editing:

| Variable | Found in | Purpose |
|---|---|---|
| `USERNAME` | Authentication | Your Rhino Health account email |
| `PROJECT_NAME` | Project Creation | Display name for the new project (currently `"Demo"`) |
| `CLIENT_DATA_PATH`, `DATASET_NAME`, `FILE_BASE_PATH` | Dataset Creation | Where the source data lives and what to call it on the platform |
| `CONTAINER_PATH`, `SCRIPT`, `CODE_OBJ_NAME` | Preprocessing Code Object Creation | Local preprocessing script location and its display name |
| `NVFLARE_CONTAINER_PATH`, `NVFLARE_OBJ_NAME` | NVFlare Training Code Object Creation | Local NVFlare app folder and its display name |

## Chart theming

Charts use Plotly with the Rhino brand palette (`RHINO_NAVY`, `RHINO_TEAL`, `RHINO_SKY`,
`RHINO_GREY`, `RHINO_AMBER`), defined once in the Setup cell along with a `DARK_MODE`
toggle:

```python
DARK_MODE = True  # ← set to False if viewing in a light-themed editor/Jupyter theme
```

`DARK_MODE` is a manual switch, not an auto-detector — flip it to match whatever
environment you're viewing the notebook in, then re-run the Setup cell and the chart
cells (no need to re-run the whole notebook) to refresh the styling.

> Some chart text (subplot titles, the significance-bar labels, the p=0.05 threshold
> line) doesn't automatically inherit `DARK_MODE`'s color and may need explicit
> `textfont`/`annotation_font_color` styling if it looks dim against a dark background.


## Additional resources

- [Rhino FCP SDK Documentation](https://rhinohealth.github.io/rhino_sdk_docs/html/autoapi/index.html)
- [Rhino FCP User Resources](https://github.com/RhinoHealth/user-resources/tree/main)
- [Rhino FCP Platform Documentation](https://docs.rhinofcp.com/)
- [NVFlare GitHub](https://github.com/NVIDIA/NVFlare/tree/main)

---
*Last updated to match notebook version validated 2026-08-11.*
