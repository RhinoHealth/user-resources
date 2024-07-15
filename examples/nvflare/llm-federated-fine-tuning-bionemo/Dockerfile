FROM nvcr.io/nvidia/clara/bionemo-framework:1.0
# Compile NeMo Megatron's helpers.cpp in advance so that it doesn't happen at runtime.
# See:
# * https://github.com/NVIDIA/NeMo/blob/bf6da5bb2f88675f2e1ed65ec34a97eaed49ff04/nemo/collections/nlp/data/language_modeling/megatron/dataset_utils.py#L1303
# * https://github.com/NVIDIA/NeMo/blob/bf6da5bb2f88675f2e1ed65ec34a97eaed49ff04/nemo/collections/nlp/data/language_modeling/megatron/Makefile
RUN make -C /usr/local/lib/python3.10/dist-packages/nemo/collections/nlp/data/language_modeling/megatron

# Install venv.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3.10-venv \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set up non-root user and group.
ARG UID=5642
ARG GID=5642
RUN ( getent group $GID >/dev/null || groupadd -r -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser
WORKDIR /home/localuser
USER localuser

ENV USER=localuser HOME=/home/localuser

# Create and "activate" venv.
ENV VIRTUAL_ENV="/home/localuser/venv"
RUN mkdir "$VIRTUAL_ENV" \
 && python -m venv --system-site-packages "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
RUN --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    export PIP_ROOT_USER_ACTION=ignore \
 && python -m pip install --upgrade pip setuptools \
 && pip install -r /requirements.txt
RUN find /usr/lib -maxdepth 1 -name '*.so' -exec bash -c 'ln -s "$(realpath {})" "$VIRTUAL_ENV/lib/$(basename {})" ' \;

RUN ln -s /opt/nvidia/bionemo/bionemo /home/localuser/venv/lib/python3.10/site-packages/bionemo

# Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID ./app ./app
COPY --chown=$UID:$GID ./meta.conf ./

# Apply a patch to NVFlare v2.4.1 to log config_fed_client on the clients.
RUN --mount=type=bind,source=log_client_config.patch,target=/log_client_config.patch \
    cd "$VIRTUAL_ENV/lib/python3.10/site-packages/nvflare" \
 && patch -p 2 < /log_client_config.patch

ENV PYTHONPATH="/home/localuser/app/custom"
ENV PYTHONUNBUFFERED=1
