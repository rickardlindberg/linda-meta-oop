#!/usr/bin/env bash

set -e

(cd rlmeta && ./make.py)

python rlmeta/rlmeta.py --support --compile examples.rlmeta --copy main.py > examples.py

python examples.py
