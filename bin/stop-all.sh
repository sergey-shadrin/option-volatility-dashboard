#!/usr/bin/env bash

set -o errexit
set -o nounset

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

APPS=$("${PROJECT_DIR}/bin/list-apps.sh")
for APP in $APPS
do
  "${PROJECT_DIR}/bin/stop-app.sh" "${APP}"
done
