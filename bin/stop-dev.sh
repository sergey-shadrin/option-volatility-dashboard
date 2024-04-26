#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_ROOT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
source "${PROJECT_ROOT_DIR}/build.env"
export RUNTIME_IMAGE_NAME

cd "${PROJECT_ROOT_DIR}" && docker-compose down --timeout 1