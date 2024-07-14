# Demo: Protein Language Model Fine-Tuning with BioNeMo and NVFlare on Rhino FCP

### Description
This example uses NVIDIA FLARE to perform federated fine-tuning of a BioNeMo ESM-style model adapted to run on Rhino Health's Federated Computing Platform (FCP).
The source of the code with explanations can be found in the [NVFlare repository](https://github.com/NVIDIA/NVFlare/blob/main/examples/advanced/bionemo/README.md).
It shows how to:
* Use BioNeMo with NVIDIA FLARE (NVFlare) and apply the necessary changes for it to run on FCP
* Package the code in a Docker container that can be used with FCP


### Resources
  * app directory: NVFlare based directory. Contains the code for the federated fine-tuning of a protein language model
  * Models: Download both the Tokenizer and the BioNeMo-Optimized Protein Language Model, placing all files into the directory `app/custom/`.
    * The Tokenizer can be downloaded from the [Huggingface repository](https://huggingface.co/facebook/esm2_t33_650M_UR50D) 
    * The BioNeMo-Optimized Protein Language Model can be downloaded from the [BioNeMo repository](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/clara/models/esm2nv650m)
  * Dockerfile: Dockerfile for building the Docker image
  * requirements.txt: Python requirements for the code
  * log_client_config.patch: Configuration file for the NVFlare client
  * meta.conf: Metadata file for the Docker image
    




