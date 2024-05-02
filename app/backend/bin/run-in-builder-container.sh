#!/usr/bin/env bash

set -o errexit

APP_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
CACHE_DIR=${1}
if [ -z "$CACHE_DIR" ];
then
  >&2 echo "Usage: run-in-builder-container.sh <cache_dir>"
  exit 1
fi

pip-compile \
  --no-header \
  --no-annotate \
  --output-file "${APP_DIR}/requirements.txt" \
  --cache-dir "${CACHE_DIR}/pip-compile" \
  "${APP_DIR}/requirements.in"
