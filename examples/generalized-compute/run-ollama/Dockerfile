FROM ollama/ollama:latest

ARG LC_ALL="C.UTF-8"
ARG TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and build dependencies
RUN --mount=type=cache,id=apt,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-dev python3.11-venv \
    && apt-get install -y libgomp1 \
    && apt-get install -y gcc python3-dev linux-headers-generic \
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
 && python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && rm requirements.txt

WORKDIR /home/localuser

COPY --chown=$UID:$GID . .
COPY --chown=$UID:$GID start.sh .
COPY --chown=$UID:$GID parse_clinical_notes.py .
RUN chmod +x start.sh
USER localuser

# This is basically what venv/bin/activate does
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

CMD ["./start.sh"]