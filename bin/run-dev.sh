#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_ROOT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

cd "${PROJECT_ROOT_DIR}" && docker-compose up -d && docker-compose logs -f