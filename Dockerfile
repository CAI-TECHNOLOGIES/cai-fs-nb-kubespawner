ARG ROOT_CONTAINER=ubuntu:focal-20200703@sha256:d5a6519d9f048100123c568eb83f7ef5bfcad69b01424f420f17c932b00dea76

ARG BASE_CONTAINER=$ROOT_CONTAINER

# Build required libraries
FROM $BASE_CONTAINER

RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    wget

RUN python3 -m pip install -U \
    setuptools \
    --no-cache-dir

COPY . cai-fs-nb-kubespawner
RUN cd cai-fs-nb-kubespawner && \
    python3 setup.py sdist --format=gztar