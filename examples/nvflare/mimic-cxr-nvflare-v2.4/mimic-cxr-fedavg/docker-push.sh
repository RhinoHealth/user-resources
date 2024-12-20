#!/bin/bash
set -eu -o pipefail


function usage() {
  echo "Usage: $0 [OPTIONS] <ecr-repo> <docker-image-tag>"
  echo
  echo "Available options:"
  echo " -f FILE                Dockerfile to use for building the container image."
  echo ' --progress STYLE       Output style to pass to `docker build`: auto (default) or plain.'
}


docker_build_args=()

while [[ $# -ne 0 ]] && [[ "$1" == -* ]]; do
  case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
  -f)
    shift
    [ $# -eq 0 ] && usage && exit 1
    docker_build_args+=("-f" "$1")
    ;;
  --progress)
    shift
    [ $# -eq 0 ] && usage && exit 1
    docker_build_args+=("--progress=$1")
    ;;
  --progress=*)
    docker_build_args+=("$1")
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

ecr_repo="$1"
docker_image_tag="$2"


ecr_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com"
container_image_uri="$ecr_registry/$ecr_repo:$docker_image_tag"

docker_build_base_cmd=(docker build --platform linux/amd64)
if [ ${#docker_build_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${docker_build_args[@]}")
fi

set -x
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --provenance=false -t "$container_image_uri" .
docker push "$container_image_uri"

{ set +x; } 2>/dev/null

echo "Done. Container image URI: $container_image_uri"
