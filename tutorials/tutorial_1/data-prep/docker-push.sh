#!/bin/bash
set -e


function usage() {
  echo "Usage: $0 <ecr-repo> <docker-image-tag>"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

if [ $# -ne 2 ]; then
  usage
  exit 0
fi

ecr_repo="$1"
docker_image_tag="$2"

ecr_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com"
full_tag="$ecr_registry/$ecr_repo:$docker_image_tag"


DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -t "$full_tag" .
docker push "$full_tag"

echo "Done. Container image URI: $full_tag"
