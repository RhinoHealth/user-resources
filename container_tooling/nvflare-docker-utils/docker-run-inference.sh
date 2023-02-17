#!/bin/bash
set -eu -o pipefail


function usage() {
  echo "Usage: $0 [OPTIONS] <input-dir> <output-dir> <weights_file_path>"
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

if [ $# -ne 3 ]; then
  usage
  exit 1
fi
input_dir="$1"
output_dir="$2"
weights_file_path="$3"


if [ ! -d "$input_dir" ]; then
  echo "No such directory: $input_dir"
  exit 1
fi
abs_input_dir="$(cd "$input_dir" && pwd -P)"
[ -d "$output_dir" ] || mkdir "$output_dir"
abs_output_dir="$(cd "$output_dir" && pwd -P)"
abs_weights_file_path="$(realpath "$weights_file_path")"

docker_build_base_cmd=(docker build)
if [ ${#dockerfile_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${dockerfile_args[@]}")
fi

SCRIPTDIR="$( cd "$(dirname "$0")" && pwd )"


set +x

DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --build-arg="UID=$(id -u)" --build-arg="GID=$(id -g)" -t "rhino-nvflare-localrun" .
docker run --rm --name rhino-nvflare-localrun-inference -v "$SCRIPTDIR/run_inference.sh:/run_inference.sh:ro" -v "$abs_weights_file_path:/model_weights:ro" -v "$abs_input_dir:/input:ro" -v "$abs_output_dir:/output" --network none rhino-nvflare-localrun "/run_inference.sh" /model_weights
