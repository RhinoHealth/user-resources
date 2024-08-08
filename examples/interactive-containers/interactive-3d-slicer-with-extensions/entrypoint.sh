#!/bin/bash
# 3D Slicer does not properly overwrite output files when they are soft links and not
# regular files. Since by default FCP sets up soft links from /output to /input, this
# causes a problem for 3D Slicer. To overcome this, we will delete the soft links in
# the /output directory and instead copy the relevant files from /input to /output as
# regular files.

set -eu -o pipefail

copy_input_to_output() {
  while IFS= read -d $'\0' -r dir ; do
    dirname="${dir#/input/}"
    cp -r "$dir" "/output/$dirname"
    # We create the standard subdirectories to maintain the original behaviour.
    [ -e "/output/$dirname/dicom_data" ] || mkdir "/output/$dirname/dicom_data"
    [ -e "/output/$dirname/file_data" ] || mkdir "/output/$dirname/file_data"
  done < <(find /input/ -mindepth 1 -maxdepth 1 -type d \( \! -name dicom_data \) \( \! -name file_data \) -print0)
}

create_backwards_compatibility_symlinks() {
  # Symlink files under /output/0/ to /output/, while creating a similar directory structure.
  [ -f /output/0/dataset.csv ] && ln -s /output/0/dataset.csv /output/dataset.csv
  [ -f /output/0/cohort_data.csv ] && ln -s /output/0/cohort_data.csv /output/cohort_data.csv
  ln -s /output/0/dicom_data /output/dicom_data
  ln -s /output/0/file_data /output/file_data
}

# Remove existing directories and symlinks under /output/, and replace them with actual files.
rm -r /output/*
copy_input_to_output
create_backwards_compatibility_symlinks

# Execute the startup script.
exec /startup.sh "$@"
