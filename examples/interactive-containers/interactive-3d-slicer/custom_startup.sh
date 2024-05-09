#!/bin/bash
# 3D Slicer does not properly overwrite output files when they are soft links and not regular files.
# Since by default FCP sets up soft links from /output to /input, this causes a problem for 3D Slicer. To overcome this, we will delete the soft links in the /output directory and instead copy the relevant files from /input to /output as regular files.
rm -r /output/*
# Now we can copy the files
cp -r /input/* /output/
exec /startup.sh
