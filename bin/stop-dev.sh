#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
APP_NAME="backend"
APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"

# TODO: надо со всех компонентов собирать необходимые переменные окружения
source "${APP_DIR}/build.env"
export RUNTIME_IMAGE_NAME

cd "${PROJECT_DIR}" && docker-compose down --timeout 1