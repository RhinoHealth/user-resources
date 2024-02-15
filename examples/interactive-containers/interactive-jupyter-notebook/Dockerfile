FROM dorowu/ubuntu-desktop-lxde-vnc:focal

# Disable VNC clipboard and selection.
RUN sed -i 's/command=x11vnc/command=x11vnc -nosel -noprimary -noclipboard/' /etc/supervisor/conf.d/supervisord.conf

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Remove Google Chrome.
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get purge -y -q --auto-remove google-chrome-stable

# Install Python 3.10
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && apt-get install -y -q curl software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update \
 && apt-get install -y -q python3.10 python3.10-dev python3.10-venv \
 && apt-get remove -y --autoremove curl software-properties-common

# Create venv.
ENV VIRTUAL_ENV="/venv"
RUN mkdir -p $VIRTUAL_ENV \
 && python3.10 -m venv $VIRTUAL_ENV

# Install Jupyter Notebook and its dependencies.
COPY requirements.txt ./
RUN "$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir --upgrade pip setuptools wheel \
 && "$VIRTUAL_ENV/bin/pip" install --no-cache-dir -r requirements.txt \
 && rm requirements.txt

# Install app menu item and desktop shortcut.
COPY ./jupyter.desktop /usr/share/applications/
COPY ./jupyter-link.desktop /root/Desktop/
COPY ./jupyter-notebook.png /usr/share/pixmaps/

RUN sed -i 's#cp -r /root/{.config,#cp -r /root/{.config,Desktop,#' /startup.sh

# Disable MIT-SHM, since 3DSlicer tries to use it by default and this causes problems.
ENV QT_X11_NO_MITSHM=1
ENV _X11_NO_MITSHM=1
ENV _MITSHM=0

# Install gnumeric
RUN apt-get update \
 && sudo apt-get -y install gnumeric

# Set up the create_dataset_csv script.
COPY ./create_dataset_csv.py /
COPY ./Create-Output-Dataset.desktop /usr/share/applications/
COPY ./Create-Output-Dataset-link.desktop /root/Desktop/
COPY ./Rhino-Health-Logo.svg /usr/share/pixmaps/
