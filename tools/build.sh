#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
.venv/bin/cmake -S vendor/lacam3 -B build/upstream -DCMAKE_BUILD_TYPE= -DCMAKE_CXX_FLAGS=-UNDEBUG
.venv/bin/cmake --build build/upstream -j2
# Upstream tests use ../assets and ../tests/assets relative to the build directory.
ln -sfn ../vendor/lacam3/assets build/assets
ln -sfn ../vendor/lacam3/tests build/tests
