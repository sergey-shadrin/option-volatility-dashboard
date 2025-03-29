#!/usr/bin/env bash

set -o errexit

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
APP_NAME=$1
if [ -z "$APP_NAME" ];
then
  >&2 echo "Usage: run-app.sh <app_name>. Possible <app_name> values are:"
  >&2 ls "${PROJECT_DIR}/app"
  exit 1
fi
APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"

cd "${APP_DIR}" && docker compose up -d