#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
APP_NAME=$1
if [ -z "$APP_NAME" ];
then
  >&2 echo "Usage: build-builder-image.sh <app_name>. Possible <app_name> values are:"
  >&2 ls "${PROJECT_DIR}/app"
  exit 1
fi

APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"

source "${APP_DIR}/build.env"

IMAGE_TAG=${BUILDER_IMAGE_NAME}
DOCKERFILE_PATH="${APP_DIR}/docker/Builder.Dockerfile"

docker build \
  --tag "${IMAGE_TAG}" \
  --file "${DOCKERFILE_PATH}" \
  "${APP_DIR}"