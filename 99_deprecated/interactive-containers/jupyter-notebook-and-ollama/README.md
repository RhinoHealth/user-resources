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


## Resources
- `explore_dataset_ollama.ipynb`: A Jupyter Notebook to explore a dataset
  and interact with an LLM model via Ollama.
- `Dockerfile`: Recipe for building the container image, based on Rhino's
  Interactive Containers base image. 
- `requirements.txt`: The required Python dependencies.
- `ollama.supervisord.conf`: Supervisord configuration file for running the
  Ollama service in the background.
- `rhino_ollama_serve.sh`: A custom wrapper script to start the Ollama
  service, enabling run-time configuration of the Ollama models directory.
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop`: Files
  for creating a desktop link to open Jupyter Notebook in a browser.


## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
