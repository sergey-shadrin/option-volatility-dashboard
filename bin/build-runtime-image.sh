#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

docker build \
  --tag shadrinsergey/option_volatility_dashboard:0.0.1 \
  --file "${PROJECT_DIR}/docker/Runtime.Dockerfile" \
  "${PROJECT_DIR}"