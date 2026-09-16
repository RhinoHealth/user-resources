# Interactive Container Example - Interactive LLM Inference

This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely run an interactive LLM inference with Jupypter Notebook session to interact with remote data on a Rhino Client

**It shows how to:**
* Structure a Dockerfile to run an interactive Jupyter Notebook
* Add links to the interactive desktop to load Jupyter Notebook
* Add a Jupyter Notebook to execute an LLM inference on the input files 
* Add a helper functions to be used by the Jupyter Notebook

## How to Run Locally

### Prerequisites
- Create a Project
- `sftp` Data to Rhino Client
- Create an FCP Dataset
- Download a model + artifacts from HuggingFace: [Using the HuggingFace CLI to Download Models and Artifacts](https://huggingface.co/docs/huggingface_hub/main/en/guides/cli)
- Upload the model + artifacts to AWS S3 to utilize the Runtime External Storage feature for Code Runs: [Using Rhino Utility to Upload Files to AWS S3](https://github.com/RhinoHealth/user-resources/blob/main/utils/upload-file-to-s3.sh)

### Build and run
To test locally, e.g. while working on changes:
1. Update `Dockerfile` and additional files.
2. Build a container image locally, then copy the resulting container image ID:
   ```shell
   DOCKER_BUILDKIT=1 docker build .
   ```
3. Run a local container using the built image. This example's base image is a CUDA-enabled desktop (`interactive-containers-base-image:ubuntu-22.04-cuda-desktop-lxde`), so `--gpus all` is needed for GPU-accelerated inference to actually use your GPU (requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to be installed on the host):
   ```shell
   docker run -p 6080:80 --gpus all <container image ID>
   ```
   * `-p 6080:80` exposes port 6080 on the host machine, so you can connect to the container's desktop.
   * `--gpus all` gives the container access to the host's GPU(s); omit it (and expect much slower inference) if you don't have a compatible GPU available locally.
4. Connect to the container via VNC using a browser by browsing to: `http://localhost:6080/`
5. From the remote desktop, use the **Jupyter Notebook** icon (or applications menu entry) to open `llm_inference.ipynb` and run inference using the helper functions in `rhino_inference_helpers.py`.
6. When done, use `../../../utils/docker-push.sh` to build and push the container image to FCP.

## Resources
- `input/`
  - `dataset.csv` - This file defines the dataset you will use as input for this project. Each row in this file represents a radiology report 
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs Jupyter Notebook and other dependencies
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop` - Files for creating a desktop link to open Jupyter Notebook
- `llm_inference.ipynb` - Jupyter Notebook used for importing helper functions to perform inference with an LLM
- `requirements.txt` - Libraries, packages, and modules required for the execution of Python scripts
- `rhino_inference_helpers.py` - Helper script with functions that are imported in Jupyter Notebook for performing inference with an LLM

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).