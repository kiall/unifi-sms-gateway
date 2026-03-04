#!/bin/bash

set -euo pipefail

sudo DEBIAN_FRONTEND=noninteractive apt-get install --yes pipx python3 python3-pip

pipx install uv

uv venv --seed --python 3.13 ${VIRTUAL_ENV}

uv pip install -U setuptools uv
uv pip install homeassistant
uv pip install tox

# Delegate to the common bootstrap script form the base image: https://github.com/home-assistant/devcontainer/blob/main/addons/rootfs/usr/bin/devcontainer_bootstrap
bash /usr/bin/devcontainer_bootstrap
