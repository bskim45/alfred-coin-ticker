#!/usr/bin/env bash
set -euo pipefail

SCRIPT_HOME=$(dirname "$(realpath "$0")")
VERSION=$(cat version)
: "${BUILD_DIR:="$SCRIPT_HOME/build"}"
: "${WORKFLOW_FILENAME:=alfred-coin-ticker.alfredworkflow}"

echo "Home path: $SCRIPT_HOME"
echo "Version: $VERSION"
echo "Build dir: $BUILD_DIR"
echo "Workflow: $WORKFLOW_FILENAME"

#read -p "Continue? [y/N]" -n 1 -r
#echo # new line
#if [[ $REPLY =~ ^[Yy]$ ]]; then
#  # pass
#  echo "Building..."
#else
#  echo "abort"
#  exit 1
#fi

rsync --archive --verbose \
  --filter '- *.pyc' \
  --filter '- *.egg-info' \
  --filter '- *.dist-info' \
  --filter '- __pycache__' \
  "$BUILD_DIR/.site-packages/" "$BUILD_DIR/"

# shellcheck disable=SC2046
cp $(<include.list) "$BUILD_DIR/"
cd "$BUILD_DIR" || exit
rm -rf "./.site-packages"

zip -r "$SCRIPT_HOME/$WORKFLOW_FILENAME" . -x@"$SCRIPT_HOME/exclude.list"
