FROM ubuntu:22.04 AS ollama-download

ADD https://github.com/ollama/ollama/releases/download/v0.1.24/ollama-linux-amd64 /ollama


FROM 913123821419.dkr.ecr.us-east-1.amazonaws.com/rhino-gc-workgroup-rhino-health-dev:rhino-ubuntu-22.04-cuda-desktop-lxde

## Disable VNC clipboard and selection.
#RUN sed -i 's/command=x11vnc/command=x11vnc -nosel -noprimary -noclipboard/' /etc/supervisor/conf.d/supervisord.conf

# Set env vars to be able to run apt-get commands without issues.
ENV LC_ALL="C.UTF-8"
ENV TZ=Etc/UTC

# Install Python 3.11 and build dependencies
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -q \
 && apt-get install -q -y software-properties-common gcc python3-dev \
 && add-apt-repository -y ppa:deadsnakes/ppa \
 && apt-get update -q \
 && apt-get install -q -y python3.11 python3.11-dev python3.11-venv \
 && apt-get remove -q -y --autoremove software-properties-common \
 && apt-get autoclean -q -y \
 && apt-get autoremove -q -y \
 && rm -rf /var/lib/apt/lists/*

# Create venv and add to PATH
ENV VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3.11 -m venv $VIRTUAL_ENV

# Install Jupyter Notebook and its dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Install Ollama.
COPY --from=ollama-download --chmod=0755 /ollama /usr/local/bin/ollama
RUN useradd -r -s /bin/false -m -d /usr/share/ollama ollama
COPY ./ollama.supervisord.conf /etc/supervisor/conf.d/ollama.conf
COPY --chmod=0755 --chown=ollama ./rhino_ollama_serve.sh /usr/share/ollama/rhino_ollama_serve.sh
ENV OLLAMA_MODELS=/external_data/ollama/models/

# Install Jupyter Notebook app menu item and desktop shortcut.
COPY ./jupyter-notebook.desktop /usr/share/applications/
COPY ./jupyter-notebook-link.desktop /root/Desktop/
COPY ./jupyter-notebook.png /usr/share/pixmaps/
