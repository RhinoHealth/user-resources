# Interactive Container Example - Interactive 3D Slicer

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive 3D Slicer session to view and/or annotate DICOM data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive 3D Slicer application
* Add links to the interactive desktop to load 3D Slicer
* Add a script to create a manifest CSV file from the 3D Slicer output files

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
   docker run -p 6080:80 -v /dev/shm:/dev/shm <container image ID>
   ```
   * `-p 6080:80` exposes port 6080 on the host machine.
   * `-v /dev/shm:/dev/shm` makes the host's `/dev/shm` mount available to the container.
     (3D Slicer requires `/dev/shm`.)
4. Connect to the container via VNC using a browser by browsing to: `http://localhost:6080/`
5. When done, use `rhino-utils/docker-push.sh` to build and push the container image to the FCP.


## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs 3D Slicer and other dependencies 
- `3D-Slicer-Mark.svg`, `3DSlicer.desktop`, `3DSlicer-link.desktop` - Files for creating a desktop link to open 3D Slicer
- `create_dataset_csv.py` - A script to create a manifest CSV file from the 3D Slicer output files
- `Rhino-Health-Logo.svg`, `Create-Output-Dataset.desktop`, `Create-Output-Dataset-link.desktop` - Files for creating a desktop link to run the create_dataset_csv.py script


## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
