#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_ROOT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

pip-compile \
  --no-header \
  --no-annotate \
  --output-file "${PROJECT_ROOT_DIR}/app/backend/requirements.txt" \
  --cache-dir "${PROJECT_ROOT_DIR}/cache/backend/pip-compile" \
  "${PROJECT_ROOT_DIR}/app/backend/requirements.in"
