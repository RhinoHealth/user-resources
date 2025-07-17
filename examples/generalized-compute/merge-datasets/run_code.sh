#!/bin/bash

DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")

set -x  # print each command (debugging)
set -e  # stop on error

python $DIR/merge_datasets.py --input_dir /input --output_dir /output
