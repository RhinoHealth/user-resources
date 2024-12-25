#!/bin/bash
set -eu -o pipefail

function usage() {
  echo "Usage: $0 [OPTIONS] <image-repo-name> <docker-image-tag>"
  echo
  echo "Available options:"
  echo " -f FILE                Dockerfile to use for building the container image."
  echo ' --progress STYLE       Output style to pass to `docker build`: auto (default) or plain.'
  echo " --rhino-domain DOMAIN  Domain to use for the registry: rhinohealth.com (default) or rhinofcp.com."
}

# Default values
default_rhino_domain="rhinohealth.com"
rhino_domain="${RHINO_DOMAIN:-$default_rhino_domain}" # Use env variable if set, otherwise use default.
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
  --rhino-domain)
    shift
    [ $# -eq 0 ] && usage && exit 1
    rhino_domain="$1"
    ;;
  *)
    echo "Unrecognized option $1."
    usage
    exit 1
    ;;
  esac
  shift
done

if [ $# -lt 2 ]; then
  usage
  exit 1
fi

image_repo_name="$1"
docker_image_tag="$2"
gcp_project_id="${3:-rhino-health-prod}" # Default gcp_project_id to "rhino-health-prod" if not provided.

# Validate rhino_domain
if [[ "$rhino_domain" != "rhinohealth.com" && "$rhino_domain" != "rhinofcp.com" ]]; then
  echo "Error: Invalid rhino-domain. Allowed values are rhinohealth.com or rhinofcp.com."
  exit 1
fi

# Set the container_image_uri based on rhino_domain
if [[ "$rhino_domain" == "rhinohealth.com" ]]; then
  image_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com"
  container_image_uri="$image_registry/$image_repo_name:$docker_image_tag"
else
  # In gcp, the image registry is specific to the project (as opposed to AWS where it's all under the infra account).
  image_registry="europe-west4-docker.pkg.dev/$gcp_project_id"
  container_image_uri="$image_registry/$image_repo_name/images:$docker_image_tag"
fi

docker_build_base_cmd=(docker build --platform linux/amd64)
if [ ${#docker_build_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${docker_build_args[@]}")
fi

set -x
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" -t "$container_image_uri" .
docker push "$container_image_uri"

{ set +x; } 2>/dev/null

echo "Done. Container image URI: $container_image_uri"
