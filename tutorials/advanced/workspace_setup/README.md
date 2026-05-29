# Workspace Setup

← set up your project, data, and collaborators

Everything needed to configure a collaborative workspace on the Rhino FCP — projects, permissions, schemas, datasets, and interactive containers.

---

## Tutorials

### Creating a Project & Configuring Permissions
Create a project, define a permissions policy, and configure project-level settings.

→ See [Tutorial 1 — Hello World](../../foundational/tutorial_1/) for a full walkthrough.
→ [docs.rhinohealth.com — Projects](https://docs.rhinohealth.com/hc/en-us/categories/24960002999453)

---

### Inviting Collaborators & Managing Access
Invite collaborators, assign roles, and configure interactive permissions for project leads and collaborators.

→ [docs.rhinohealth.com — Collaborators](https://docs.rhinohealth.com/hc/en-us/categories//24960002999453)

---

### Defining Data Schemas
Define input/output schemas with field types and permissions.

→ See [Tutorial 1 schemas](../../foundational/tutorial_1/schemas/).
→ [docs.rhinohealth.com — Data Schemas](https://docs.rhinohealth.com/hc/en-us/categories/24960002999453)

---

### Importing Datasets (CSV, DICOM, S3, SQL)
Import local CSV and DICOM data; connect to S3 and SQL databases at run time.

→ [`../../../../examples/rhino-sdk/sql-data-ingestion.ipynb`](../../../../examples/rhino-sdk/sql-data-ingestion.ipynb)
→ [`../../../../examples/rhino-sdk/runtime_external_files.ipynb`](../../../../examples/rhino-sdk/runtime_external_files.ipynb)

---

## Interactive Containers

Launch browser-accessible GUI environments on the FCP for data exploration and analysis without exporting data.

| Container | Description |
|---|---|
| [Jupyter Notebook](../../../../examples/interactive-containers/interactive-jupyter-notebook/) | Interactive Jupyter environment |
| [3D Slicer](../../../../examples/interactive-containers/interactive-3d-slicer/) | Medical imaging analysis GUI |
| [3D Slicer with Extensions](../../../../examples/interactive-containers/interactive-3d-slicer-with-extensions/) | 3D Slicer with DCMQI, PET, and annotation extensions |
| [QuPath](../../../../examples/interactive-containers/interactive-qupath/) | Pathology image analysis GUI |
| [LLM Inference (Jupyter + Ollama)](../../../../examples/interactive-containers/jupyter-notebook-and-ollama/) | Run local LLM inference on federated data |
| [LibreOffice](../../../../examples/interactive-containers/libre-office/) | Document editing |

See [`../../../../examples/interactive-containers/`](../../../../examples/interactive-containers/) for all container Dockerfiles and READMEs.

---

## Note on folder structure

Sub-folders for each topic may be added here as dedicated tutorial notebooks, videos, or additional assets are created. The README above covers all current content.

---

## Additional resources

- [Tutorial 1 — Hello World](../../foundational/tutorial_1/)
- [docs.rhinohealth.com — Using the Rhino FCP GUI](https://docs.rhinohealth.com/hc/en-us/categories/24960002999453)
