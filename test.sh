#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  ./update.sh
fi
# shellcheck source=/dev/null
source .venv/bin/activate
export PYTHONPATH="${PWD}/src"
python -m unittest discover -s tests -v
