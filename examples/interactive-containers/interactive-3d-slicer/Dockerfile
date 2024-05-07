FROM dorowu/ubuntu-desktop-lxde-vnc:focal

# Disable VNC clipboard and selection.
RUN sed -i 's/command=x11vnc/command=x11vnc -nosel -noprimary -noclipboard/' /etc/supervisor/conf.d/supervisord.conf

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Remove Google Chrome.
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get purge -y -q --auto-remove google-chrome-stable

# Install 3DSlicer dependencies.
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && apt-get install -y -q libpulse-dev libnss3 libglu1-mesa wget \
 && apt-get install -y -q --reinstall libxcb-xinerama0 \
 && apt-get -y -q install libxcb-icccm4-dev libxcb-image0-dev \
    libxcb-keysyms1-dev libxcb-randr0 libxcb-render-util0 libxcb-xkb-dev libxkbcommon-x11-dev

# Install 3DSlicer (version 5.2.2 from 2023-02-22).
RUN mkdir -p /opt/slicer \
 && wget -q -O /tmp/slicer.tar.gz https://slicer-packages.kitware.com/api/v1/item/63f5bee68939577d9867b4c7/download \
 && tar -xzf /tmp/slicer.tar.gz --strip-components=1 --directory /opt/slicer/ \
 && rm /tmp/slicer.tar.gz \
 && ln -s /opt/slicer/Slicer /usr/bin/Slicer
COPY ./3DSlicer.desktop /usr/share/applications/
COPY ./3DSlicer-link.desktop /root/Desktop/
COPY ./3D-Slicer-Mark.svg /usr/share/pixmaps/
RUN sed -i 's#cp -r /root/{.config,#cp -r /root/{.config,Desktop,#' /startup.sh
ENV PATH "$PATH:/opt/slicer"

# Disable MIT-SHM, since 3DSlicer tries to use it by default and this causes problems.
ENV QT_X11_NO_MITSHM=1
ENV _X11_NO_MITSHM=1
ENV _MITSHM=0

# Set up the create_dataset_csv script.
COPY ./create_dataset_csv.py /

# Set up Desktop and applications menu shortcuts.
COPY ./Create-Output-Dataset.desktop /usr/share/applications/
COPY ./Create-Output-Dataset-link.desktop /root/Desktop/
COPY ./Rhino-Health-Logo.svg /usr/share/pixmaps/

# Update the ENTRYPOINT to execute both scripts
ENTRYPOINT ["custom_startup.sh"]