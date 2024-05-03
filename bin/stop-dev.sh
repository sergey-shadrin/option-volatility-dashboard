#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
# TODO: надо со всех компонентов собирать необходимые переменные окружения

source "${PROJECT_DIR}/app/backend/build.env"
BACKEND_RUNTIME_IMAGE_NAME=${RUNTIME_IMAGE_NAME}
export BACKEND_RUNTIME_IMAGE_NAME

source "${PROJECT_DIR}/app/frontend/build.env"
FRONTEND_RUNTIME_IMAGE_NAME=${RUNTIME_IMAGE_NAME}
export FRONTEND_RUNTIME_IMAGE_NAME

cd "${PROJECT_DIR}" && docker-compose down --timeout 1