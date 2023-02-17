Rhino Health NVFLARE Dev Tools
==============================

***Tools for local development of container images for running NVFLARE-based FL in the Rhino Health Platform.***


# Why Use This?

* Iterate quickly while developing locally.
* Emulate the conditions of the Rhino Health Platform, to help ensure your container images will work there.
* These tools take care of many small details for you.  Some are crucial, such as building container images for the
  correct architecture (amd64, not ARM).  Some make local development faster and nicer, such as re-using local caches
  for `pip install` and `apt-get install`, and not running containers as a root user.
* `docker-run.sh --auto` completely automates setting up a local NVFLARE server and local client(s) and running FL
  training with them, saving you the time and effort of doing so repeatedly (and of learning how!).


# Requirements

1. Bash shell available at `/bin/bash` (the common default location)
2. [Docker](https://docs.docker.com/get-docker/)


# Included Tools

Run each tool with `-h` or `--help` for usage details.

1. `docker-run.sh`: Run FL training with your code using, locally, using Docker.  Recommended: `--auto`.
2. `docker-run-inference.sh`: Run inference with your code on a single dataset.
3. `docker-push.sh`: Push your code packaged in a container image to a container image repository.

Additionally, the `examples` directory includes complete working examples of NVFLARE-based FL models.
These are useful for making sure the tooling works on your machine, and as a starting point for
containerizing your own code.


# Step by Step Outline

## Development

1. Adapt your FL client code to read all inputs from `/input`.
   See [Input Data Directory Structure](#input-data-directory-structure) for details.
2. Adapt your FL server code to write output model parameters (weight, biases etc.) to a file named
   `model_parameters.*` under `/output`.  For example: `/output/model_parameters.pt`.
3. List the Python dependencies of your code in a `requirements.txt` file.
4. Copy `examples/hello-numpy-sag/Dockerfile` and make changes as needed where there are comments beginning with
   `# !! EDIT THIS:`.
5. Test by building and running the container locally:

   ```shell
   cd path/to/your/code
   path/to/scripts/docker-run.sh --auto path/to/input path/to/output
   ```

6. Debug and repeat until it works...


## Uploading to the Rhino Cloud

1. Sign in to AWS using the AWS CLI:
   1. Only the time: Create an AWS SSO profile: `aws sso configure` (you'll set a profile name here)
   2. `aws sso login --profile <profile-name>`
   3. `aws ecr get-login-password --region us-east-1 --profile awsinfra | docker login --username AWS --password-stdin 913123821419.dkr.ecr.us-east-1.amazonaws.com`
2. Find the Rhino ECR repo name for your workgroup, e.g. `rhino-gc-workgroup-rhinohealthdev`
3. Choose a unique tag for this container image, e.g. `rhino-nvflare-hello-numpy-sag-v1`
4. Build and push the container to the Rhino ECR repo using `docker-push.sh`.  For example:

   ```shell
   cd path/to/your/code
   path/to/scripts/docker-push.sh rhino-gc-workgroup-rhinohealthdev rhino-nvflare-hello-numpy-sag-v1
   ```

# Input Data Directory Structure

For each input cohort...

* Its data will be found in a subdirectory of `/input`, whose name is the cohort UID.
  For example: `/input/00000000-0000-0000-0000-000000000000`. 
* Its tabular data will be in a file named `cohort_data.csv`.
* If present, its DICOM data will be in files under a `dicom_data` directory.
* If present, its files for "Filename" column values will be in files under a `file_data` directory.
