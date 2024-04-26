#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

source "${PROJECT_DIR}/build.env"

docker build \
  --tag ${BASE_IMAGE_NAME} \
  --file "${PROJECT_DIR}/app/backend/docker/Base.Dockerfile" \
  "${PROJECT_DIR}/app/backend"