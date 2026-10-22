#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
# Optional research-licensed comparator; inspect its license before redistribution.
if [ ! -d vendor/mapf-lns2/.git ]; then
    git clone https://github.com/Jiaoyang-Li/MAPF-LNS2.git vendor/mapf-lns2
    git -C vendor/mapf-lns2 checkout 1369823985a15944f9a339226d521f61605a6d17
fi
test "$(git -C vendor/mapf-lns2 rev-parse HEAD)" = 1369823985a15944f9a339226d521f61605a6d17
# Eigen 3.x and Boost are required; modern Eigen 5 is not a compatible substitute.
# On macOS: brew install boost eigen@3; set CMAKE_PREFIX_PATH accordingly.
.venv/bin/cmake -S vendor/mapf-lns2 -B build/lns2 -DCMAKE_BUILD_TYPE=Release
.venv/bin/cmake --build build/lns2 -j2
