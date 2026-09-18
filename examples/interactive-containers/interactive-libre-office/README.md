# Interactive Container Example - LibreOffice

These are the sources for a container image with LibreOffice to be used as a Rhino FCP
interactive container.

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
5. From the remote desktop, use the **LibreOffice** icon (or applications menu entry) to launch LibreOffice and interact with your data.
6. When done, use `../../../utils/docker-push.sh` to build and push the container image to FCP.

## Resources
- `Dockerfile`: Recipe for building the container image, based on Rhino's
  Interactive Containers base image. 
- `libreoffice-logo.png`, `libreoffice.desktop`, `libreoffice-link.desktop`: Files
  for creating a desktop link to open LibreOffice.


## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
