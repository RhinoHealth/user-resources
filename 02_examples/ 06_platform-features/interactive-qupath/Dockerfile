FROM dorowu/ubuntu-desktop-lxde-vnc:focal

# Disable VNC clipboard and selection.
RUN sed -i 's/command=x11vnc/command=x11vnc -nosel -noprimary -noclipboard/' /etc/supervisor/conf.d/supervisord.conf

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Remove Google Chrome.
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get purge -y -q --auto-remove google-chrome-stable

# Clean up.
ENV DEBIAN_FRONTEND=""

# Install QuPath (v0.4.3 from 2023-02-23).
RUN mkdir -p /opt \
 && cd ${TMPDIR:-/tmp} \
 && curl -sSL -o ./QuPath-0.4.3-Linux.tar.xz https://github.com/qupath/qupath/releases/download/v0.4.3/QuPath-0.4.3-Linux.tar.xz \
 && tar -xf ./QuPath-0.4.3-Linux.tar.xz \
 && rm ./QuPath-0.4.3-Linux.tar.xz \
 && chmod +x ./QuPath/bin/QuPath ./QuPath/bin/QuPath.sh \
 && mv ./QuPath /opt/QuPath \
 && ln -s /opt/QuPath/bin/QuPath /usr/local/bin/QuPath \
 && ln -s /opt/QuPath/bin/QuPath.sh /usr/local/bin/QuPath.sh

# Install gnumeric
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && sudo apt-get -y install gnumeric

# Install app menu item and desktop shortcut.
COPY ./QuPath.desktop /usr/share/applications/
COPY ./QuPath-link.desktop /root/Desktop/
COPY ./qupath_128.png /usr/share/pixmaps/

RUN sed -i 's#cp -r /root/{.config,#cp -r /root/{.config,Desktop,#' /startup.sh

# Set up the create_dataset_csv script.
COPY ./create_dataset_csv.py /
COPY ./Create-Output-Dataset.desktop /usr/share/applications/
COPY ./Create-Output-Dataset-link.desktop /root/Desktop/
COPY ./Rhino-Health-Logo.svg /usr/share/pixmaps/
