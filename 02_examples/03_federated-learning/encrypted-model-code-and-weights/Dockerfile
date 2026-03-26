FROM python:3.8-slim-bullseye

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

# Copy code.
COPY --chown=$UID:$GID ./config ./config
COPY --chown=$UID:$GID ./custom ./custom
COPY --chown=$UID:$GID ./entrypoint.sh ./entrypoint.sh
COPY --chown=$UID:$GID ./infer.py ./infer.py

ENV PYTHONPATH="/home/localuser/custom"
ENV PYTHONUNBUFFERED=1

# Use a custom entrypoint to decrypt code before executing commands.
# Ensure files are executable.
RUN chmod +x ./infer.py
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]