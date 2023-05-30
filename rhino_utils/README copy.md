# Utilities for creating Rhino Generalized Compute container images using Docker


## Step by Step Outline

### Development

1. Adapt your code to read all inputs from `/input` and write all results to `/output`.
   The tabular data shall be in files named `cohort_data.csv` under each of these directories.
2. List the Python dependencies of your code in a `requirements.txt` file.
   Recommended: Use "pinned dependencies" as described in the [Python Dependencies section](Python Dependencies).
3. Copy `example/Dockerfile` and make changes as need where there are comments beginning with: "# !! EDIT THIS:".
4. Test by building and running the container locally:
   
   `./docker-run.sh path/to/input path/to/output`

   Debug and repeat until it works...

### Uploading to the Rhino Cloud

1. Sign in to AWS using the AWS CLI:
   1. Only the time: Create an AWS SSO profile: `aws sso configure` (you'll set a profile name here)
   2. `aws sso login --profile <profile-name>`
   3. `aws ecr get-login-password --region us-east-1 --profile awsinfra | docker login --username AWS --password-stdin 913123821419.dkr.ecr.us-east-1.amazonaws.com`
2. Choose a name to attach to the container as a "tag".
3. Find the Rhino Generalized Compute ECR repo name for your workgroup.
   
   For example: `rhino-gc-workgroup-rhinohealthdev`
4. Build and push the container to the Rhino ECR repo:
   
   `./docker-push.sh <ecr-repo-name> <your-tag>`


## Contents

1. `docker-run.sh`: Build a docker container image and run it locally.
2. `docker-push.sh`: Build a docker container image and push it to a container image repository.
3. `example`: Complete working example of `Dockerfile` and `requirements.in` files.
4. `compile-requirements.sh`: Utility script for creating `requirements.txt` files with pinned dependencies.


## Building and Running a Container Image

```shell
docker-run.sh <input-dir> <output-dir>
```

This does a few things specific to local builds:

1. Use Docker BuildKit to use the local pip cache.
2. Make the docker container run as the local user to avoid creating files and dirs owned by root.


## Python Dependencies

We highly recommend the following method for specifying dependencies:
1. List only direct dependencies in `requirements.in`, with the appropriate version or range of supported versions.
2. Generate `requirements.txt` by running the included `compile-requirements.sh` script.

This will list specific versions in `requirements.txt`, of all direct and indirect Python dependencies.
This practice is called "pinning" dependencies. This ensures that all future installations will use exactly the same
versions of the same dependencies. 
