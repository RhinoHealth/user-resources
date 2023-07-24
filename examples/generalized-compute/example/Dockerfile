# !! EDIT THIS: Set base Docker image to be used.
FROM python:3.6.13-slim-stretch

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

WORKDIR /home/localuser
USER localuser

# !! EDIT THIS: Copy the needed local files (code and otherwise) into the container work directory.
# Note: For directories, have a separate COPY command for each top-level directory.
COPY --chown=$UID:$GID dcm2png.py merge_manifest.py runprep.sh ./

# !! EDIT THIS: Ensure files are executable.
RUN chmod +x dcm2png.py merge_manifest.py runprep.sh

ENV PYTHONUNBUFFERED=1

# !! EDIT THIS: Set the command to be executed when the container is run, with arguments as needed.
CMD ["./runprep.sh", "/input", "/output", "/input/cohort_data.csv"]
