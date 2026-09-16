# NVIDIA FLARE Example: Protein Language Model Fine-Tuning with BioNeMo

## Description
This example uses NVIDIA FLARE to perform federated fine-tuning of a BioNeMo ESM-style model adapted to run on Rhino's Federated Computing Platform (FCP). The model source code with explanations can be found in the [NVFlare repository](https://github.com/NVIDIA/NVFlare/blob/main/examples/advanced/bionemo/README.md).

**This example shows how to:**
* Use BioNeMo with NVIDIA FLARE (NVFlare) and apply the necessary changes for it to run on FCP
* Package the code in a Docker container that can be used with FCP

## Resources
- `app` - NVFlare job folder, deployed to every site per `meta.conf`'s `deploy_map`
  - `config` - The standard NVFlare directory for config files
    - `config_fed_client.conf` - The NVFlare federated client config
    - `config_fed_server.conf` - The NVFlare federated server config
  - `custom` - The standard NVFlare directory for custom model code
    - `base_config.yaml` - The base BioNeMo/NeMo training configuration shared across model sizes
    - `pretrain_esm2_8M.yaml`, `pretrain_esm2_650M.yaml`, `pretrain_esm2_3B.yaml`, `pretrain_esm2_15B.yaml` - Per-model-size pretraining configs for each ESM-2 variant
    - `downstream_flip.py` - Preprocesses FLIP downstream-task data (via `bionemo.data.FLIPPreprocess`) ahead of fine-tuning
    - `downstream_flip_scl.yaml` - Fine-tuning config for the FLIP subcellular-localization (SCL) downstream task
    - *(You need to add)* the Tokenizer and BioNeMo-Optimized Protein Language Model files here yourself - see "Models" below
- `Dockerfile` - The Dockerfile used for building the container image, based on NVIDIA's `bionemo-framework` base image
- `log_client_config.patch` - A patch to NVFlare 2.4.1 to log `config_fed_client` on the clients
- `meta.conf` - NVFlare job metadata (`deploy_map`, `min_clients`) - required by FCP's provisioning; FCP reads this straight from the running container, so it must exist at the container's WORKDIR
- `README.md` - This file
- `requirements.txt` - The Python requirements for this project

### Models
Before building the image, download both of the following into `app/custom/`:
- The Tokenizer, from the [Huggingface repository](https://huggingface.co/facebook/esm2_t33_650M_UR50D)
- The BioNeMo-Optimized Protein Language Model, from the [BioNeMo repository](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/clara/models/esm2nv650m)

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
