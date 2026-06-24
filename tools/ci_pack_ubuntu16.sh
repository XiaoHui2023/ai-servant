#!/usr/bin/env bash
set -euo pipefail

cd /work
rm -rf .venv build dist

apt-get update
apt-get install -y --no-install-recommends ca-certificates wget bzip2 binutils patchelf

MINICONDA=Miniconda3-py310_23.5.2-0-Linux-x86_64.sh
wget -q "https://repo.anaconda.com/miniconda/${MINICONDA}" -O "/tmp/${MINICONDA}"
bash "/tmp/${MINICONDA}" -b -p /opt/conda
export PATH="/opt/conda/bin:${PATH}"

python -m venv .venv
bash tools/pack.sh src
