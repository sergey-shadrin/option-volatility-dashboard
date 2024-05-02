#!/usr/bin/env bash

set -o errexit

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
APP_NAME=$1
if [ -z "$APP_NAME" ];
then
  >&2 echo "Usage: build-project.sh <app_name>. Possible <app_name> values are:"
  >&2 ls "${PROJECT_DIR}/app"
  exit 1
fi
APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"
APP_CACHE_DIR="${PROJECT_DIR}/cache/${APP_NAME}"

"${PROJECT_DIR}/bin/run-builder-container.sh" "${APP_NAME}" bash -c "${APP_DIR}/bin/run-in-builder-container.sh ${APP_CACHE_DIR}"