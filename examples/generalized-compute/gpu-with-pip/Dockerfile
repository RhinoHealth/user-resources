# !! EDIT THIS: Set base Docker image to be used.
FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

# Set env vars to be able to run apt-get commands without issues.
ARG LC_ALL="C.UTF-8"
ARG TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.8
RUN --mount=type=cache,id=apt,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean \
 && apt-get update \
 && apt-get install -y -q software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update \
 && apt-get install -y -q python3.8 python3.8-dev python3.8-venv \
 && apt-get remove -y --autoremove software-properties-common \
 && apt-get -y install curl \
 && apt-get install libgomp1 \
 && rm -rf /var/lib/apt/lists/*

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
 && python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && rm requirements.txt



WORKDIR /home/localuser

COPY --chown=$UID:$GID . .
USER localuser

# This is basically what venv/bin/activate does
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

CMD [ "python", "cupy_preprocessing.py"]

