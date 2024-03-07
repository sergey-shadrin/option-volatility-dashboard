#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

docker build \
  --tag option_volatility_dashboard_builder:0.0.1 \
  --file "${PROJECT_DIR}/docker/Builder.Dockerfile" \
  "${PROJECT_DIR}"