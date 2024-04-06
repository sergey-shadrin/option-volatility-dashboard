#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR="$(dirname "$(readlink -f "$0")")"

cd "${PROJECT_DIR}"

docker compose pull && \
  docker compose down && \
  docker compose up -d
