#!/usr/bin/env bash

set -o errexit

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
APP_NAME=$1
if [ -z "$APP_NAME" ];
then
  >&2 echo "Usage: run-builder-container.sh <app_name>. Possible <app_name> values are:"
  >&2 ls "${PROJECT_DIR}/app"
  exit 1
fi
APP_DIR="${PROJECT_DIR}/app/${APP_NAME}"
shift # this is required to strip APP_NAME from command line arguments
source "${APP_DIR}/build.env"

USER_ID=$(id -u)

docker run \
  --rm \
  --interactive \
  --tty \
  --user "$USER_ID" \
  --volume "/etc/passwd:/etc/passwd:ro" \
  --volume "/etc/group:/etc/group:ro" \
  --volume "$PWD:$PROJECT_DIR" \
  --workdir "$PROJECT_DIR" \
  "$BUILDER_IMAGE_NAME" \
  "$@"
