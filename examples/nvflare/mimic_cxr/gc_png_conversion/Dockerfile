# !! EDIT THIS: Set base Docker image to be used.
FROM python:3.8-bullseye

ARG UID=5642
ARG GID=5642

# Set up non-root user and group.
RUN ( getent group $GID >/dev/null || groupadd -r -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser \
 && mkdir /venv \
 && chown $UID:$GID /venv
WORKDIR /home/localuser
USER localuser

# Create and "activate" venv.
ENV VIRTUAL_ENV="/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
COPY requirements.txt ./
RUN --mount=type=cache,target=/home/localuser/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && rm requirements.txt

# !! EDIT THIS: Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID run_dataprep.py ./

# !! EDIT THIS: Ensure files are executable.
RUN chmod +x run_dataprep.py

ENV PYTHONUNBUFFERED=1

# !! EDIT THIS: Set the command to be executed when the container is run, with arguments as needed.
CMD ["./run_dataprep.py", "/input", "/output", "/input/cohort_data.csv"]
