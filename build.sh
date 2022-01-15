#!/usr/bin/env bash

WORKFLOW_NAME=alfred-coin-ticker.alfredworkflow

SCRIPT_HOME=$(dirname "$(realpath "$0")")
VERSION=$(cat version)

echo "Home path: $SCRIPT_HOME"
echo "Version: $VERSION"

cd "$SCRIPT_HOME/alfred-workflow/workflow" || exit
git clean -nx

read -p "Continue? [y/N]" -n 1 -r
echo # new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
  git clean -fx
else
  echo "abort"
  exit 1
fi

cd "$SCRIPT_HOME" || exit
rm -f $WORKFLOW_NAME
zip -r $WORKFLOW_NAME -@ <includes.list
