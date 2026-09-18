# Interactive Container Example - Interactive Jupyter Notebook

This example provides files that can be used with the Rhino FCP Generalized Compute capability to remotely run an interactive Jupypter Notebook session to interact with remote data on a Rhino Client

**It shows how to:**
* Structure a Dockerfile to run an interactive Jupyter Notebook
* Add links to the interactive desktop to load Jupyter Notebook
* Add a script to create a manifest CSV file from the Jupyter Notebook output files

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Interactive Container capability.

## How to Run Locally
To test locally, e.g. while working on changes:
1. Update `Dockerfile` and additional files.
2. Build a container image locally, then copy the resulting container image ID:
   ```shell
   DOCKER_BUILDKIT=1 docker build .
   ```
3. Run a local container using the built image:
   ```shell
   docker run -p 6080:80 <container image ID>
   ```
   * `-p 6080:80` exposes port 6080 on the host machine, so you can connect to the container's desktop.
4. Connect to the container via VNC using a browser by browsing to: `http://localhost:6080/`
5. From the remote desktop, use the **Jupyter Notebook** icon (or applications menu entry) to launch Jupyter Notebook and do your work. When you're done producing output files, use the separate **Create Output Dataset** icon to run `create_dataset_csv.py` and generate the manifest CSV for them.
6. When done, use `../../../utils/docker-push.sh` to build and push the container image to FCP.

## Resources
- `create_dataset_csv.py` - A script to create a manifest CSV file from the Jupyter Notebook output files
- `Create-Output-Dataset.desktop`, `Create-Output-Dataset-link.desktop`, `Rhino-Logo.svg` - Files for creating a desktop link to run the create_dataset_csv.py script
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs Jupyter Notebook and other dependencies 
- `jupyter-notebook.png`, `jupyter.desktop`, `jupyter-link.desktop` - Files for creating a desktop link to open Jupyter Notebook
- `requirements.txt` - dependencies

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
