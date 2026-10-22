#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
.venv/bin/python tools/fetch_pibt.py
.venv/bin/cmake -S vendor/pibt-tiebreaking/one-shot -B build/pibt -DCMAKE_BUILD_TYPE= -DCMAKE_CXX_FLAGS=-UNDEBUG
.venv/bin/cmake --build build/pibt -j2
