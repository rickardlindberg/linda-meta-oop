#!/usr/bin/env bash

set -e

if [ -n "$(git status -s)" ]; then
    git status
    exit 1
fi

git clean -f -d -x

./make.sh

git push
