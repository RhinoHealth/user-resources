#!/bin/bash
set -e


function usage() {
  echo "Usage: $0 <input-dir> <output-dir>"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

if [ $# -ne 2 ]; then
  usage
  exit 0
fi

input_dir="$1"
output_dir="$2"

abs_input_dir=$(cd "$input_dir" && pwd -P)
[ -d "$output_dir" ] || mkdir "$output_dir"
abs_output_dir=$(cd "$output_dir" && pwd -P)


DOCKER_BUILDKIT=1 docker build --build-arg="UID=$(id -u)" --build-arg="GID=$(id -g)" -t "rhino-gc-localrun" .

exec docker run -it -v "$abs_input_dir:/input:ro" -v "$abs_output_dir:/output" --network none "rhino-gc-localrun"
