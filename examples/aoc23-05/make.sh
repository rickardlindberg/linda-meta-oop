#!/usr/bin/env bash

set -e

python ../../rlmeta/rlmeta.py --support --compile ../../rlmeta/src/stdlib.rlmeta --compile puzzle.rlmeta --main > puzzle.py

python puzzle.py
