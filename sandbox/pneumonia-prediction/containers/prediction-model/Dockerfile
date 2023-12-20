# !! EDIT THIS: Set the version of Python to be used.
FROM python:3.8-bullseye as wheelbuilder

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -U pip setuptools wheel \
 && pip wheel --cache-dir=/.cache/pip --wheel-dir /wheels -r requirements.txt



# !! EDIT THIS: Set the version of Python to be used.
FROM python:3.8-slim-bullseye

COPY --from=wheelbuilder /wheels /wheels
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /venv \
 && . /venv/bin/activate \
 && python -m pip install -U pip setuptools wheel \
 && pip install --no-cache /wheels/*

ARG UID=5642
ARG GID=5642

RUN ( getent group $GID >/dev/null || groupadd -g $GID localgroup ) \
 && useradd -m -l -s /bin/bash -g $GID -N -u $UID localuser \
 && chown -R $UID:$GID /venv
WORKDIR /home/localuser
USER localuser

COPY ./config ./config
COPY ./custom ./custom
COPY ./infer.py ./infer.py

# This is basically what venv/bin/activate does
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"
ENV PYTHONPATH="/home/localuser/custom"
