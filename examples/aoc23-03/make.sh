#!/usr/bin/env bash

set -e

python ../../rlmeta/rlmeta.py --support --compile puzzle.rlmeta --copy main.py > puzzle.py

python puzzle.py "$@"
