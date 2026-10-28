FROM nvcr.io/nvidia/cuda:13.0.2-runtime-ubuntu24.04

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Install Python 3.12.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -qq \
 && apt-get install -q -y --no-install-recommends -q python3 python3-dev python3-venv

# Set up non-root user and group.
ARG UID=5642
ARG GID=5642
RUN ( getent group $GID >/dev/null || groupadd -r -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser

# Create and "activate" venv.
ENV VIRTUAL_ENV="/venv"
RUN mkdir $VIRTUAL_ENV \
 && chmod g+s $VIRTUAL_ENV \
 && chown $UID:$GID $VIRTUAL_ENV \
 && python3.12 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    export PIP_ROOT_USER_ACTION=ignore \
 && python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && rm requirements.txt

WORKDIR /home/localuser
USER localuser

# Download the DenseNet-121 ImageNet weights at build time: FL pods may have no internet access.
ENV TORCH_HOME="/home/localuser/torch_home"
RUN python -c "import torchvision; torchvision.models.densenet121(weights='DEFAULT')"

# Copy code.
COPY --chown=$UID:$GID ./app ./app/
COPY --chown=$UID:$GID ./meta.json ./

ENV PYTHONPATH="/home/localuser/app/custom"
ENV PYTHONUNBUFFERED=1
# Staggering: the FL client pods that share a GPU agent don't request a GPU, so the node's runtime exposes the GPU
# to this container only when these are set.
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
