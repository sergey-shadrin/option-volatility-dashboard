#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

cd "${PROJECT_DIR}" && docker-compose up -d && docker-compose logs -f