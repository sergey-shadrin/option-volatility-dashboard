#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_ROOT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

"${PROJECT_ROOT_DIR}/bin/run-builder-container.sh" bash -c ./bin/run-in-builder-container.sh