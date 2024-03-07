#!/usr/bin/env bash

set -o errexit
set -o nounset

WORK_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DOCKER_IMAGE=option_volatility_dashboard_builder:0.0.1
USER_ID=$(id -u)

docker run \
  --rm \
  --interactive \
  --tty \
  --user "$USER_ID:www-data" \
  --volume "/etc/passwd:/etc/passwd:ro" \
  --volume "/etc/group:/etc/group:ro" \
  --volume "$PWD:$WORK_DIR" \
  --workdir "$WORK_DIR" \
  "$DOCKER_IMAGE" \
  "$@"
