# Rhino FCP Examples

This folder contains grab-and-go reference implementations for specific Rhino Federated Computing Platform (FCP) capabilities - working code you can copy from and adapt, organized by capability rather than as a guided lesson. If you're looking for more detailed step-by-step walkthroughs, see [`../tutorials/`](../tutorials/README.md).

## Categories

- **[`generalized-compute/`](./generalized-compute/README.md)** - Generalized Compute (GC) code objects: containerized data processing patterns like DICOM-to-PNG conversion, extracting DICOM tags, merging/splitting datasets, GPU-accelerated compute (conda and pip variants), running encrypted code, and train/test splitting.
- **[`interactive-containers/`](./interactive-containers/README.md)** - Interactive Container sessions for live, no-code interaction with remote data on a Rhino Client - 3D Slicer, QuPath, Jupyter Notebook, LLM inference via Ollama, and LibreOffice.
- **[`nvflare/`](./nvflare/README.md)** - Federated learning via NVIDIA FLARE (NVFlare) on FCP. Ranges from "hello world" scatter-and-gather demos (`hello-numpy-sag`, `hello-pt`), through regression models (logistic/linear, Poisson, quantile, GLM), PyTorch/XGBoost/MONAI training, encrypted model code and weights, and larger federated fine-tuning workflows (BioNeMo LLM fine-tuning).
- **[`rhino-sdk/`](./rhino-sdk/README.md)** - Standalone notebooks demonstrating specific Rhino Python SDK capabilities outside of a tutorial narrative: federated joins, federated statistics/EDA, differentially-private quantiles, Cox proportional hazards, SQL-based dataset ingestion, object CRUD (create/update), and Streamlit-based visualization.
- **[`site-testing-financial/`](./site-testing-financial/README.md) / [`site-testing-life-science/`](./site-testing-life-science/README.md)** - Site validation scripts that confirm a newly installed Rhino Client can complete an end-to-end project (dataset import, a Generalized Compute run, an NVFlare Autocontainer run) - a financial-data and a life-science-data variant of the same validation workflow.

## Also useful

- [`../utils/`](../utils/README.md) - Shared shell scripts referenced by many of the examples above, most commonly `docker-push.sh` for building and pushing a container image to your workgroup's registry.

# Getting Help

For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
