#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then uv venv .venv --python 3.12; fi
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python tools/fetch_upstream.py
sh tools/build.sh
printf 'Activate with: source .venv/bin/activate\nThen run: python tools/check.py\n'
