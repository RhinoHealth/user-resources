# !! EDIT THIS: Set base Docker image to be used.
FROM nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Install Python 3.10
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -qq \
 && apt-get install -q -y --no-install-recommends -q software-properties-common \
 && add-apt-repository -y ppa:deadsnakes/ppa \
 && apt-get update -qq \
 && apt-get install -q -y --no-install-recommends -q python3.10 python3.10-dev python3.10-venv \
 && apt-get remove -q -y --autoremove software-properties-common

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
 && python3.10 -m venv --upgrade-deps $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    PIP_ROOT_USER_ACTION=ignore pip install -r /requirements.txt

WORKDIR /home/localuser
USER localuser

# !! EDIT THIS: Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID ./app ./app
COPY --chown=$UID:$GID ./infer.py ./meta.json ./

ENV PYTHONPATH="/home/localuser/app/custom"
ENV PYTHONUNBUFFERED=1
