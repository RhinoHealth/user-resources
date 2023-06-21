# !! EDIT THIS: Set the version of Python to be used.

FROM python:3.8-slim-bullseye as wheelbuilder

COPY requirements.txt ./

RUN --mount=type=cache,target=/.cache/pip \
    python -m pip install -U pip setuptools wheel \
 && pip wheel --no-deps --cache-dir=/.cache/pip --wheel-dir /wheels -r requirements.txt



# !! EDIT THIS: Set the version of Python to be used.
FROM python:3.8-bullseye

COPY --from=wheelbuilder /wheels /wheels
RUN python -m venv /venv \
 && . /venv/bin/activate \
 && python -m pip install --no-cache -U pip setuptools wheel \
 && pip install --no-cache /wheels/*

ARG UID=1001
ARG GID=1001

RUN groupadd -r -g $GID localgroup \
 && useradd -ms /bin/bash -g localgroup -u $UID localuser \
 && chown -R localuser:localgroup /venv
WORKDIR /home/localuser
USER localuser

COPY dataprep_gc.py run_dataprep.sh ./

# This is basically what venv/bin/activate does
ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"


CMD ["./run_dataprep.sh", "/input", "/output", "/input/cohort_data.csv"]
