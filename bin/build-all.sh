#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

# Build 'builder' Docker image which has all dependencies to build current project
"${PROJECT_DIR}/bin/build-builder-image.sh"

# Build project in project root directory
"${PROJECT_DIR}/bin/build-project.sh"

# Build 'base' Docker image which has all dependencies except app
"${PROJECT_DIR}/bin/build-base-image.sh"

# Build 'runtime' Docker image upon 'base' Docker image by copying app files in it
"${PROJECT_DIR}/bin/build-runtime-image.sh"