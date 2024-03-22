#!/usr/bin/env bash

set -o errexit
set -o nounset

RUNTIME_IMAGE_TAG="shadrinsergey/option_volatility_dashboard:0.0.1"

PROJECT_DIR="$(dirname "$(readlink -f "$0")")"

cd "${PROJECT_DIR}"

docker pull "${RUNTIME_IMAGE_TAG}" && \
  docker compose down && \
  docker compose up -d
