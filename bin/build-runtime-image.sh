#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
source "${PROJECT_DIR}/build.env"

docker build \
  --build-arg "BASE_IMAGE_NAME=${BASE_IMAGE_NAME}" \
  --tag "${RUNTIME_IMAGE_NAME}" \
  --file "${PROJECT_DIR}/docker/Runtime.Dockerfile" \
  "${PROJECT_DIR}"

docker push "${RUNTIME_IMAGE_NAME}"