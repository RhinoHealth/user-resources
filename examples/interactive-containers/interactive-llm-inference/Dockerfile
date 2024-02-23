FROM ubuntu:22.04 as lmstudio-appimage-download

ADD --chmod=744 https://releases.lmstudio.ai/linux/0.2.14/beta/LM_Studio-0.2.14-beta-1.AppImage /LM_Studio-0.2.14-beta-1.AppImage

FROM 913123821419.dkr.ecr.us-east-1.amazonaws.com/rhino-gc-workgroup-rhino-health-dev:rhino-ubuntu-22.04-cuda-desktop-lxde

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Install Python 3.11.
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
RUN --mount=type=cache,mode=0755,id=pip,target=/root/.cache/pip,sharing=locked \
    --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    "$VIRTUAL_ENV/bin/python" -m pip install --upgrade pip setuptools wheel \
 && "$VIRTUAL_ENV/bin/pip" install -r /requirements.txt

# Install LM Studio.
RUN --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -q \
 && apt-get install -q -y libnss3 pciutils
RUN --mount=type=bind,from=lmstudio-appimage-download,source=/LM_Studio-0.2.14-beta-1.AppImage,target=/LM_Studio.AppImage \
    mkdir /LM_Studio \
 && cd /LM_Studio \
# See: https://docs.appimage.org/user-guide/run-appimages.html#extract-the-contents-of-an-appimage
 && /LM_Studio.AppImage --appimage-extract \
 && chmod a+x ./squashfs-root/lm-studio \
 && chmod -R a+rw . \
 && find . -type d -exec chmod a+x {} +

# Install Jupyter Notebook app menu item and desktop shortcut.
COPY ./jupyter-notebook.desktop /usr/share/applications/
COPY ./jupyter-notebook-link.desktop /root/Desktop/
COPY ./jupyter-notebook.png /usr/share/pixmaps/

# Upload notebook
Copy ./explore_dataset.ipynb /root/Desktop/

# Install LM Studio app menu item and desktop shortcut.
COPY ./lmstudio.desktop /usr/share/applications/
COPY ./lmstudio-link.desktop /root/Desktop/
COPY ./lmstudio-icon.png /usr/share/pixmaps/

# Upload llm model
RUN mkdir -p /home/localuser/.cache/lm-studio/models/TheBloke/Mistral-7B-Instruct-v0.2-code-ft-GGUF
COPY ./mistral-7b-instruct-v0.2-code-ft.Q8_0.gguf /home/localuser/.cache/lm-studio/models/TheBloke/Mistral-7B-Instruct-v0.2-code-ft-GGUF/
