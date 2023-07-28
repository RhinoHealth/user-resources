#FROM continuumio/miniconda3:4.12.0  as envbuilder
FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04 as envbuilder

# Installation of some libraries / RUN some commands on the base image
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,id=apt,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean \
 && apt-get update \
 && apt-get install -y -q --no-install-recommends wget \
 && rm -rf /var/lib/apt/lists/*

# Declare some ARGuments
ARG CONDA_VERSION=3
ARG CONDA_PY_VERSION=py37_23.1.0-1

# INSTALLATION OF CONDA
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda$CONDA_VERSION-$CONDA_PY_VERSION-Linux-x86_64.sh -O ~/miniconda.sh \
 && /bin/bash ~/miniconda.sh -b -p /opt/conda \
 && rm ~/miniconda.sh \
 && /opt/conda/bin/conda clean --all --quiet --yes \
 && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
# && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
# && echo "conda activate base" >> ~/.bashrc

COPY environment.yml ./
RUN --mount=type=cache,target=/opt/conda/pkgs \
    /opt/conda/bin/conda env create -p /env -f environment.yml \
 && rm environment.yml




FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

# Installation of some libraries / RUN some commands on the base image
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,id=apt,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean \
 && apt-get update \
 && apt-get install -y -q --no-install-recommends wget \
 && rm -rf /var/lib/apt/lists/*

# Declare some ARGuments
ARG CONDA_VERSION=3
ARG CONDA_PY_VERSION=py37_23.1.0-1

# INSTALLATION OF CONDA
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda$CONDA_VERSION-$CONDA_PY_VERSION-Linux-x86_64.sh -O ~/miniconda.sh \
 && /bin/bash ~/miniconda.sh -b -p /opt/conda \
 && rm ~/miniconda.sh \
 && /opt/conda/bin/conda clean --all --quiet --yes \
 && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
# && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
# && echo "conda activate base" >> ~/.bashrc

ARG UID=5642
ARG GID=5642

RUN ( getent group $GID >/dev/null || groupadd -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser

COPY --from=envbuilder --chown=$UID:$GID /env /env

# See: https://github.com/ContinuumIO/docker-images/issues/151#issuecomment-549742754
RUN chgrp $GID /opt/conda/pkgs && \
    chmod g+w /opt/conda/pkgs && \
    touch /opt/conda/pkgs/urls.txt && \
    chown $UID:$GID /opt/conda/pkgs/urls.txt

ENV PATH /opt/conda/bin:$PATH

WORKDIR /home/localuser
COPY --chown=$UID:$GID . .
USER localuser

# !! EDIT THIS: Set the command to be executed when the container is run, with arguments as needed.
ENTRYPOINT ["conda", "run", "--no-capture-output", "-p", "/env"]
CMD ["python", "cudf_preprocessing.py"]
