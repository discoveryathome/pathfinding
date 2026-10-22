FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git clang make cmake zlib1g-dev ca-certificates && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir uv
WORKDIR /pilot
COPY . .
RUN sh tools/setup.sh
CMD [".venv/bin/python", "tools/check.py"]
