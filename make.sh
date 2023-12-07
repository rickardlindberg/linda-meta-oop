#!/usr/bin/env bash

set -e

(cd rlmeta && ./make.py)

find examples/*/make.sh -executable | while read x; do
    dir=$(dirname $x)
    script=$(basename $x)
    (cd $dir && echo $dir && ./$script)
done

python rlmeta/rlmeta.py --support --compile examples.rlmeta --copy main.py > examples.py
python examples.py

echo "OK"
