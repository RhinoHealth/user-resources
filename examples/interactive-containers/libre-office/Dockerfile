# Begin with the base image for Interactive Containers
FROM public.ecr.aws/u7h0g2s9/rhino/interactive-containers-base-image:ubuntu-22.04-cuda-desktop-lxde

## Disable VNC clipboard and selection.
RUN sed -i 's/command=x11vnc/command=x11vnc -nosel -noprimary -noclipboard/' /etc/supervisor/conf.d/supervisord.conf

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Install LibreOffice
RUN apt-get update -q && apt-get install -q -y libreoffice

# Install LibreOffice app menu item and desktop shortcut.
COPY ./libreoffice.desktop /usr/share/applications/
COPY ./libreoffice-link.desktop /root/Desktop/
COPY ./libreoffice-logo.png /usr/share/pixmaps/
