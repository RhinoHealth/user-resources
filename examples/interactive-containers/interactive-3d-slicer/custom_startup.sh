#!/bin/bash
# 3D Slicer does not properly overwrite output files when they are soft links and not regular files.
# Since by default FCP sets up soft links from /output to /input, this causes a problem for 3D Slicer. To overcome this, we will delete the soft links in the /output directory and instead copy the relevant files from /input to /output as regular files.
rm -r /output/*
# Copy the input directory content to the output directory.

mkdir -p /output/0/dicom_data
mkdir -p /output/0/files_data

cp -r /input/0/dicom_data/* /output/0/dicom_data/
cp -r /input/0/files_data/* /output/0/files_data/

# Create the directory structure in the destination directory
cd "/output/0/dicom_data" || exit
find . -type d -exec mkdir -p "/output/dicom_data/{}" \;

# Create symbolic links for all files
find . -type f -exec ln -s "/output/0/dicom_data/{}" "/output/dicom_data/{}" \;

# Create the directory structure in the destination directory
cd "/output/0/files_data" || exit
find . -type d -exec mkdir -p "/output/files_data/{}" \;

# Create symbolic links for all files
find . -type f -exec ln -s "/output/0/files_data/{}" "/output/files_data/{}" \;

exec /startup.sh
