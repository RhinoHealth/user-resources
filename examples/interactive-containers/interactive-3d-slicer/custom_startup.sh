#!/bin/bash
# 3D Slicer does not properly overwrite output files when they are soft links and not regular files.
# Since by default FCP sets up soft links from /output to /input, this causes a problem for 3D Slicer. To overcome this, we will delete the soft links in the /output directory and instead copy the relevant files from /input to /output as regular files.

rm -r /output/*

# Now we can copy the files and dicoms
cp -r /input/0/* /output/0/
cp -r /input/dicom_data/* /output/dicom_data/
cp -r /input/file_data/* /output/file_data/

exec /startup.sh
