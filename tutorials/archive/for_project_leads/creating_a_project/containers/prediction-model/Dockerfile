FROM python:3.10-slim-bullseye

# Force rebuild - Version 16 with enhanced debugging
ARG UID=5642
ARG GID=5642
RUN ( getent group $GID >/dev/null || groupadd -r -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser

ENV VIRTUAL_ENV="/venv"
RUN mkdir $VIRTUAL_ENV \
    && chmod g+s $VIRTUAL_ENV \
    && chown $UID:$GID $VIRTUAL_ENV \
    && python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    PIP_ROOT_USER_ACTION=ignore \
    pip install --upgrade pip setuptools wheel \
    && pip install -r /requirements.txt

WORKDIR /home/localuser
USER localuser

# Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID ./app ./app/
COPY --chown=$UID:$GID ./infer.py ./meta.conf ./   

ENV PYTHONPATH="/home/localuser/app/custom"
ENV PYTHONUNBUFFERED=1
