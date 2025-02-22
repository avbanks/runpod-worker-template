# Base image -> https://github.com/runpod/containers/blob/main/official-templates/base/Dockerfile
# DockerHub -> https://hub.docker.com/r/runpod/base/tags
FROM runpod/base:0.6.2-cuda12.4.1

# The base image comes with many system dependencies pre-installed to help you get started quickly.
# Please refer to the base image's Dockerfile for more information before adding additional dependencies.
# IMPORTANT: The base image overrides the default huggingface cache location.


# --- Optional: System dependencies ---
# COPY builder/setup.sh /setup.sh
# RUN /bin/bash /setup.sh && \
#     rm /setup.sh
RUN apt-get update && apt-get upgrade -y # Update System

# Install System Dependencies
# - openssh-server: for ssh access and web terminal
RUN apt-get install -y --no-install-recommends \
    software-properties-common \
    gcc \
    g++ \
    make \
    curl \
    git \
    openssh-server \
    nvidia-container-toolkit \
    espeak-ng \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3.10-venv

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3.10 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip for Python 3.10
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py

# Clean up, remove unnecessary packages and help reduce image size
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY builder/requirements.txt /requirements.txt
RUN python3.10 -m pip install --upgrade pip && \
    python3.10 -m pip install --upgrade -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

RUN pip3 install llvmlite --ignore-installed
RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Install RunPod and TTS
RUN pip3 install --no-cache-dir runpod TTS

# Clean up pip cache
RUN rm -rf /root/.cache/pip

# NOTE: The base image comes with multiple Python versions pre-installed.
#       It is reccommended to specify the version of Python when running your code.

# Add src files (Worker Template)
ADD src .

CMD ["python", "-u", "/handler.py"]
