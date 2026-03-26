FROM dorowu/ubuntu-desktop-lxde-vnc:focal

FROM public.ecr.aws/u7h0g2s9/rhino/interactive-containers-base-image:ubuntu-22.04-cuda-desktop-lxde

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# # Install Python 3.11.
RUN --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
 && export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -q \
 && apt-get install -q -y software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update -q \
 && apt-get install -q -y python3.11 python3.11-dev python3.11-venv \
 && apt-get remove -q -y --autoremove software-properties-common \
 && apt-get autoclean -q -y \
 && apt-get autoremove -q -y

# Create venv.
ENV VIRTUAL_ENV="/venv"
RUN mkdir -p $VIRTUAL_ENV \
 && python3.11 -m venv $VIRTUAL_ENV 

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

# Copy files to the container.
COPY ./rhino_inference_helpers.py /root/Desktop/
COPY ./llm_inference.ipynb /root/Desktop
