#!/usr/bin/env bash

set -o errexit

PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

ls "${PROJECT_DIR}/app"