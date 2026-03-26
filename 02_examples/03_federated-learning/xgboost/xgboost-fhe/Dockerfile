FROM python:3.10-slim-bullseye

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
 && python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && rm requirements.txt

# Build encryption plugins
RUN apt-get update
RUN apt install -y g++ libgmp3-dev make
RUN pip install cmake==3.22.1
COPY ./vendor/encryption_plugins ./encryption_plugins/
ENV CMAKE_MAKE_PROGRAM="make"
ENV CMAKE_CXX_COMPILER="g++"
RUN cd encryption_plugins/build/ && \
    cmake .. && \
    make
ENV NVFLARE_XGB_PLUGIN_NAME=nvflare
ENV NVFLARE_XGB_PLUGIN_PATH=/encryption_plugins/build/nvflare_plugin/libnvflare.so

WORKDIR /home/localuser
USER localuser

# !! EDIT THIS: Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID ./app ./app/
COPY --chown=$UID:$GID ./meta.json ./

ENV PYTHONPATH="/home/localuser/app/custom"
ENV PYTHONUNBUFFERED=1
