#!/bin/bash

if [ $# -ne 3 ]; then
  >&2 echo "Usage: $0 input_dir output_dir csv_file"
  exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2
CSV_FILE=$3

DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")

set -x
set -e

python $DIR/dcm2png.py --input_dir ${INPUT_DIR} --output_dir ${OUTPUT_DIR}/data --output_folder png
python $DIR/merge_manifest.py --ehr_csv ${CSV_FILE} --manifest_csv ${OUTPUT_DIR}/data/png/manifest.csv --merged_csv ${OUTPUT_DIR}/data/merged.csv

cp ${OUTPUT_DIR}/data/merged.csv ${OUTPUT_DIR}/dataset.csv
