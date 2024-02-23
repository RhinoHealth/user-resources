# Interactive Container Example - Interactive LLM Inference

This example provides files that can be used with the Rhino Health Generalized Compute capability to interact with llm model via open-interpreter with remote data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive Jupyter Notebook with LLM
* Add links to the interactive desktop to load Jupyter Notebook and LM Studio
* Add a jupyter notebook to explore dataset and execute simple ETL

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Interactive Container capability.

## How to Run Locally



## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs Jupyter Notebook, LM Studio and other dependencies 
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop` - Files for creating a desktop link to open Jupyter Notebook
- `lm-studio.png`, `lm-studio.desktop`, `lm-studio-link.desktop` - Files for creating a desktop link to open LM Studio
- `explore_dataset.ipynb` - A jupyter notebook to explore dataset and execute simple ETL
- `mistral-7b-instruct-v0.2-code-ft.Q8_0.gguf.fake` - A dummy file containing the LLM model
- `requirements.txt` - A file containing the python dependencies for the dataset exploration jupyter notebook


## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
