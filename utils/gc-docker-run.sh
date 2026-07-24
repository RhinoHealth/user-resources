#!/bin/bash
set -eu -o pipefail


function usage() {
  echo "Usage: $0 [OPTIONS] <input-dir> <output-dir>"
  echo
  echo "Available options:"
  echo " -f FILE                Dockerfile to use for building the container image."
}


dockerfile_args=()

while [[ $# -ne 0 ]] && [[ "$1" == -* ]]; do
  case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
  -f)
    shift
    [ $# -eq 0 ] && usage && exit 1
    dockerfile_args=("-f" "$1")
    ;;
  *)
    echo "Unrecognized option $1."
    usage
    exit 1
    ;;
  esac
  shift
done

if [ $# -ne 2 ]; then
  usage
  exit 0
fi

input_dir="$1"
output_dir="$2"


[ -d "$output_dir" ] || mkdir "$output_dir"
if [ -n "$(ls -A "$output_dir")" ]; then
  echo 'Output directory must be empty.'
  exit 1
fi

if command -v python3 &> /dev/null; then
  python_cmd=python3
elif command -v python &> /dev/null; then
  python_cmd=python
else
  echo "Can not find python executable; exiting."
fi

abs_input_dir=$(cd "$input_dir" && pwd -P)
abs_output_dir=$(cd "$output_dir" && pwd -P)


# Prepare script for mirroring input data in the output directory.
create_output_symlinks_script="$(mktemp)_create_output_symlinks.py"
cat > "$create_output_symlinks_script" <<EOF
#!/usr/bin/env python
"""Mirror dicom_data and file_data from input_dir to output_dir.

This creates a directory tree containing relative symbolic links to the input files.
"""
import os
import posixpath
import sys

input_dir, output_dir = sys.argv[1:]

def count_path_parts(path):
    count = 1 + path.count(os.sep)
    if os.altsep:
        count += path.count(os.altsep)
    return count

for dirname in ["dicom_data", "file_data"]:
    input_data_dir = os.path.join(input_dir, dirname)
    if not os.path.exists(input_data_dir):
        continue
    output_data_dir = os.path.join(output_dir, dirname)
    os.makedirs(output_data_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_data_dir, topdown=True):
        for filename in files:
            input_file_full_path = os.path.join(root, filename)
            input_file_path_relative_to_data_dir = os.path.relpath(input_file_full_path, input_data_dir)

            output_file_full_path = os.path.join(output_dir, dirname, input_file_path_relative_to_data_dir)
            output_file_parent_full_path = os.path.dirname(output_file_full_path)
            os.makedirs(output_file_parent_full_path, exist_ok=True)

            # This will be something similar to "../../input/file_data/some_file_1"
            depth = count_path_parts(input_file_path_relative_to_data_dir) - 1
            relative_symlink_target_path = \
                posixpath.join(*([".."] * (depth + 2)), "input", dirname, input_file_path_relative_to_data_dir)

            os.symlink(relative_symlink_target_path, output_file_full_path)
EOF
chmod +x "$create_output_symlinks_script"


# Prepare script for rewriting output data symbolic links.
rewrite_output_symlinks_script="$(mktemp)_rewrite_output_symlinks.py"
cat > "$rewrite_output_symlinks_script" <<EOF
#!/usr/bin/env python
"""Rewrite symlinks under dicom_data and file_data in the output_dir."""
import os
import posixpath
import re
import sys

input_dir, output_dir = sys.argv[1:]


for dirname in ["dicom_data", "file_data"]:
    input_data_dir = os.path.join(input_dir, dirname)
    output_data_dir = os.path.join(output_dir, dirname)
    if not os.path.exists(output_data_dir):
        continue

    for root, dirs, files in os.walk(output_data_dir, topdown=True):
        for filename in files:
            output_file_full_path = os.path.join(root, filename)
            if not os.path.islink(output_file_full_path):
                continue
            link_path = os.readlink(output_file_full_path)
            without_parent_dirs = re.sub(r"^(\.\./)+", "", link_path)
            link_path_parts = without_parent_dirs.split("/")
            without_output_and_data_dir = link_path_parts[2:]
            expected_link_path = \
                posixpath.join(*([".."] * (len(link_path_parts) - 1)), "input", dirname, *without_output_and_data_dir)
            if link_path == expected_link_path:
                input_file_full_path = os.path.join(input_data_dir, *without_output_and_data_dir)
                os.unlink(output_file_full_path)
                os.symlink(input_file_full_path, output_file_full_path)
EOF
chmod +x "$rewrite_output_symlinks_script"


docker_build_base_cmd=(docker build)
if [ ${#dockerfile_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${dockerfile_args[@]}")
fi


set -x

# Build the container.
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --build-arg="UID=$(id -u)" --build-arg="GID=$(id -g)" -t "rhino-gc-localrun" .

# Mirror dicom_data and file_data from /input to /output.
$python_cmd "$create_output_symlinks_script" "$abs_input_dir" "$abs_output_dir"

# Run the container.
docker run -it -v "$abs_input_dir:/input:ro" -v "$abs_output_dir:/output" --network none "rhino-gc-localrun"

# Rewrite symlinks in output data dirs to absolute paths on the local file system.
$python_cmd "$rewrite_output_symlinks_script" "$abs_input_dir" "$abs_output_dir"
