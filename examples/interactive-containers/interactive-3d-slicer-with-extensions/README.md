# Interactive Container Example - Interactive 3D Slicer with Extensions

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive 3D Slicer session to view and/or annotate DICOM data on a Rhino Client. It also includes several extensions that allow a user to save their output as DICOM images instead of NIfTI.

It shows how to:
* Structure a Dockerfile to run an interactive 3D Slicer application
* Download and install 3DSlicer extensions in the Dockerfile
* Add a link to the desktop to run 3D Slicer
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
- `extensions/` - tarball files for each extension that we want to include within our image.  **Since this container uses version 5.2.2 of 3D-Slicer your extensions must also be version 5.2.2.  For the repository of extensions and Slicer versions follow the link [here](https://slicer-packages.kitware.com/#collection/5f4474d0e1d8c75dfc70547e/folder/63f5c7358939577d9867b86b)**
- `install-slicer-extension.py` - A script to install the extensions that you would like to add to the container. **Modify the hard-coded extension names with the ones you would like to install**
<br><br>

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
