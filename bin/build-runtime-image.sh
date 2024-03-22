#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
RUNTIME_IMAGE_TAG="shadrinsergey/option_volatility_dashboard:0.0.1"

docker build \
  --tag "${RUNTIME_IMAGE_TAG}" \
  --file "${PROJECT_DIR}/docker/Runtime.Dockerfile" \
  "${PROJECT_DIR}"

docker push "${RUNTIME_IMAGE_TAG}"