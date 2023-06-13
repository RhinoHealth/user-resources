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

python $DIR/dataprep_gc.py --input_csv ${CSV_FILE} --input_dir ${INPUT_DIR} --output_dir ${OUTPUT_DIR}

if [ -e ${INPUT_DIR}/dicom_data/ ] && [ -n "$(ls -A ${INPUT_DIR}/dicom_data/)" ] && ! [ -n "$(ls -A ${OUTPUT_DIR}/dicom_data/)" ]
  then cp -r ${INPUT_DIR}/dicom_data/* ${OUTPUT_DIR}/dicom_data/
fi
if [ -e ${INPUT_DIR}/file_data/ ] && [ -n "$(ls -A ${INPUT_DIR}/file_data/)" ] && ! [ -n "$(ls -A ${OUTPUT_DIR}/file_data/)" ]
  then cp -r ${INPUT_DIR}/file_data/* ${OUTPUT_DIR}/file_data/
fi
