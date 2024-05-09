#!/bin/bash
# The content of /output is soft links to files in /input, hence copy will be skipped - so we delete the output dir first
rm -r /output/*
# Now we can copy the files
cp -r /input/* /output/
exec /startup.sh
