# Interactive Container Example - Jupyter Notebook + Ollama

These are the sources for a container image to be used as a Rhino FCP
interactive container.


## Ollama Background Service
This runs an Ollama service in the background in the container. The Ollama
service loads its models from the directory set in the "OLLAMA_MODELS" key in
the run params, or falls back to the value set in the "OLLAMA_MODELS"
environment variable. The default value for this is
"/external_data/ollama/models/".

To create such a models dir, one needs to run Ollama locally, download one or
more models via ollama pull <model>, then upload the local Ollama models dir
(e.g. $HOME/.ollama/models) to the S3 bucket for runtime external files.


## How to Run Locally
To test locally, e.g. while working on changes:
1. Update `Dockerfile` and additional files.
2. Build a container image locally, then copy the resulting container image ID:
   ```shell
   DOCKER_BUILDKIT=1 docker build .
   ```
3. Make an Ollama models directory available, matching the `OLLAMA_MODELS` default path above. If you don't already have one locally, run Ollama locally and `ollama pull <model>` first to populate `$HOME/.ollama/models`.
4. Run a local container using the built image. This example's base image is a CUDA-enabled desktop, so `--gpus all` is needed for GPU-accelerated inference (requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to be installed on the host):
   ```shell
   docker run -p 6080:80 --gpus all \
     -v $HOME/.ollama/models:/external_data/ollama/models \
     <container image ID>
   ```
   * `-p 6080:80` exposes port 6080 on the host machine, so you can connect to the container's desktop.
   * `--gpus all` gives the container access to the host's GPU(s); omit it (and expect much slower inference) if you don't have a compatible GPU available locally.
   * `-v $HOME/.ollama/models:/external_data/ollama/models` mounts your local Ollama models into the path `OLLAMA_MODELS` defaults to - adjust the host-side path if your models live elsewhere.
5. Connect to the container via VNC using a browser by browsing to: `http://localhost:6080/`
6. From the remote desktop, use the **Jupyter Notebook** icon (or applications menu entry) to open `explore_dataset_ollama.ipynb` and interact with the model via Ollama.
7. When done, use `../../../utils/docker-push.sh` to build and push the container image to FCP.


## Resources
- `Dockerfile`: Recipe for building the container image, based on Rhino's
  Interactive Containers base image. 
- `explore_dataset_ollama.ipynb`: A Jupyter Notebook to explore a dataset
  and interact with an LLM model via Ollama.
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop`: Files
  for creating a desktop link to open Jupyter Notebook in a browser.
- `ollama.supervisord.conf`: Supervisord configuration file for running the
  Ollama service in the background.
- `requirements.txt`: The required Python dependencies.
- `rhino_ollama_serve.sh`: A custom wrapper script to start the Ollama
  service, enabling run-time configuration of the Ollama models directory.


## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
