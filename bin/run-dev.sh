#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
# TODO: надо со всех компонентов собирать необходимые переменные окружения
APP_NAME="backend"
APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"

source "${APP_DIR}/build.env"
BACKEND_RUNTIME_IMAGE_NAME=${RUNTIME_IMAGE_NAME}
export BACKEND_RUNTIME_IMAGE_NAME

cd "${PROJECT_DIR}" && docker-compose up -d && docker-compose logs -f