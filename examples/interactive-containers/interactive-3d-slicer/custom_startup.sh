#!/bin/bash
# 3D Slicer does not properly overwrite output files when they are soft links and not regular files.
# Since by default FCP sets up soft links from /output to /input, this causes a problem for 3D Slicer. To overcome this, we will delete the soft links in the /output directory and instead copy the relevant files from /input to /output as regular files.

create_symlinks_dir() {
  local dir_type=$1

  local input_dir="/input/0/$dir_type"
  local output_files_dir="/output/0/$dir_type"
  local output_link_dir="/output/$dir_type"

  # We create the directory even if its is empty to maintain the original behaviour
  mkdir -p "$output_files_dir"

  if [ "$(ls -A "$input_dir")" ]; then

    # Copy the files from the input/0 directory to the output/0 directory
    cp -r "$input_dir"/* "$output_files_dir"

    # Create the same directory structure in the dirs that will contain the links
    cd "$output_files_dir"
    find . -type d -exec mkdir -p "$output_link_dir/{}" \;

    # Create links to found files
    find . -type f -exec ln -s "$output_files_dir/{}" "$output_link_dir/{}" \;
  fi
}

rm -r /output/*

create_symlinks_dir "dicom_data"
create_symlinks_dir "file_data"

# Execute the startup script
exec /startup.sh
