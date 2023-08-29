#!/bin/bash
set -eu -o pipefail


function usage() {
  echo "Usage: $0 [OPTIONS] <input-dir> <output-dir>"
  echo
  echo "Available options:"
  echo " -f FILE                Dockerfile to use for building the container image."
  echo ' --progress STYLE       Output style to pass to `docker build`: auto (default) or plain.'
  echo ' --platform PLATFORM    Platform to build container for, e.g. "linux/amd64",'
  echo '                          via `docker build --platform=PLATFORM`'
  echo " --n-clients NUM        Number of clients to run. (default: $n_clients)"
  echo " --timeout-seconds NUM  Maximum duration for application to run. (default: $timeout_seconds)"
  echo " --auto                 Automatically drive the training via the admin API"
  echo ' --gpus GPUS            GPUs to make available to all containers, via `docker run --gpus=GPUS`'
}


docker_build_args=()
build_platform="linux/amd64"
docker_run_args=()
n_clients=1
timeout_seconds=600
auto=0

while [[ $# -ne 0 ]] && [[ "$1" == -* ]]; do
  case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
  -f)
    shift
    [ $# -eq 0 ] && usage && exit 1
    docker_build_args=("-f" "$1")
    ;;
  --progress)
    shift
    [ $# -eq 0 ] && usage && exit 1
    docker_build_args+=("--progress=$1")
    ;;
  --progress=*)
    docker_build_args+=("$1")
    ;;
  --platform)
    shift
    [ $# -eq 0 ] && usage && exit 1
    build_platform="$1"
    ;;
  --platform=*)
    build_platform="${1#--platform=}"
    ;;
  --n-clients)
    shift
    [ $# -eq 0 ] && usage && exit 1
    n_clients="$1"
    ;;
  --timeout-seconds)
    shift
    [ $# -eq 0 ] && usage && exit 1
    timeout_seconds="$1"
    ;;
  --auto)
    auto=1
    ;;
  --gpus)
    shift
    [ $# -eq 0 ] && usage && exit 1
    docker_run_args+=("--gpus" "$1")
    ;;
  --gpus=*)
    docker_run_args+=("$1")
    ;;
  *)
    echo "Unrecognized option $1."
    usage
    exit 1
    ;;
  esac
  shift
done

docker_build_args+=(--platform "$build_platform")


if [ $# -ne 2 ]; then
  usage
  exit 1
fi

input_dir="$1"
output_dir="$2"


if [ $auto -eq 0 ]; then
  if [ -e "fl_admin.sh" ]; then
    echo "fl_admin.sh already exists; aborting"
    exit 1
  fi
  if [ -e "fl_terminate.sh" ]; then
    echo "fl_terminate.sh already exists; aborting"
    exit 1
  fi
fi

if [ ! -d "$input_dir" ]; then
  echo "No such directory: $input_dir"
  exit 1
fi
abs_input_dir="$(cd "$input_dir" && pwd -P)"
[ -d "$output_dir" ] || mkdir "$output_dir"
abs_output_dir="$(cd "$output_dir" && pwd -P)"


if [ -e ./config/config_fed_server.json.bak ]; then
  mv ./config/config_fed_server.json.bak ./config/config_fed_server.json
fi
sed -i.bak 's/"min_clients"[[:space:]]*:[[:space:]]*[0-9][0-9]*/"min_clients": '$n_clients'/' ./config/config_fed_server.json
docker_build_base_cmd=(docker build)
if [ ${#docker_build_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${docker_build_args[@]}")
fi
uid=$(id -u)
gid=$(id -g)
set -x
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --build-arg="UID=$uid" --build-arg="GID=$gid" -t "rhino-nvflare-localrun" .
{ set +x; } 2>/dev/null
mv ./config/config_fed_server.json.bak ./config/config_fed_server.json

tmpdir="$(mktemp -d)"
if [ ! -d $tmpdir ]; then
  echo "Failed to create temporary directory"
  exit 1
fi
echo "Created temporary directory: $tmpdir"


nvflare_version="$(docker run --rm --network none "rhino-nvflare-localrun" pip freeze | grep '^nvflare==' | cut -d= -f3)"
IFS='.' read -r -a nvflare_version_parts <<< "$nvflare_version"
if [[ "$nvflare_version" == 2.0.* ]]; then
  nvflare_server_connection_str="rhino-nvflare-localrun-server"
elif [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]]; then
  nvflare_server_connection_str="rhino-nvflare-localrun-server:8002:8002"
else
  echo >&2 "Only versions 2.0, 2.2 and 2.3 of NVFLARE are supported."
  exit 1
fi

# temporary shim for unzip because NVFlare's poc.py requires it
cat > $tmpdir/unzip << EOF
#!/bin/sh
if [ "\$1" = "-q" ]; then
  shift
fi
if [ \$# -ne 1 ]; then
  echo "Error in unzip shim!"
  exit 1
fi
exec python -m zipfile -e "\$1" .
EOF
chmod +x $tmpdir/unzip
cat > $tmpdir/prep_poc.sh << EOF
#!/bin/sh
if [ "${nvflare_version_parts[1]}" -eq 0 ]; then
  echo y | poc -n "$n_clients" >/dev/null
elif [ "${nvflare_version_parts[1]}" -eq 2 ] || [ "${nvflare_version_parts[1]}" -eq 3 ]; then
  export NVFLARE_POC_WORKSPACE=/tmp/nvflare/poc
  echo y | nvflare poc --prepare -n "$n_clients" >/dev/null
  mv /tmp/nvflare/poc/* poc/
else
  echo >&2 "Only versions 2.0, 2.2 and 2.3 of NVFLARE are supported."
  exit 1
fi
EOF
chmod +x $tmpdir/prep_poc.sh
mkdir $tmpdir/poc
if ! docker run --rm -v "$tmpdir/unzip:/home/localuser/bin/unzip" -v "$tmpdir/prep_poc.sh:/home/localuser/bin/prep_poc.sh" -v "$tmpdir/poc:/home/localuser/poc" --network none "rhino-nvflare-localrun" /bin/sh -c 'PATH=/home/localuser/bin:$PATH prep_poc.sh '"$n_clients"; then
  rc=$?
  echo 'Running NVFlARE'"'"'s poc script failed.'
  echo 'Make sure NVFLARE is installed in the container,'
  echo 'and that the `poc` executable is available on $PATH in the container.'
  exit $rc
fi
chmod +x "$tmpdir/poc/server/startup/sub_start.sh"
for clientnum in $(seq 1 "$n_clients"); do
  chmod +x "$tmpdir/poc/site-$clientnum/startup/sub_start.sh"
done
chmod +x "$tmpdir/poc/admin/startup/fl_admin.sh"
if [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]]; then
  find "$tmpdir/poc/" -type f -name 'fed_*.json' \
    -exec sed -i.bak 's/localhost:8002/rhino-nvflare-localrun-server:8002/' {} \; \
    -exec rm {}.bak \;
fi

if ! docker network ls | tail -n +2 | awk '{ print $2 }' | grep -q '^rhino-nvflare-localrun$'; then
  docker network create --internal rhino-nvflare-localrun
fi

mkdir "$tmpdir/tb-logs"
mkdir "$tmpdir/tb-logs/server"
for clientnum in $(seq 1 "$n_clients"); do
  mkdir "$tmpdir/tb-logs/client-$clientnum"
done

docker_run_base_cmd=(docker run --rm)
if [ ${#docker_run_args[@]} -gt 0 ]; then
  docker_run_base_cmd+=("${docker_run_args[@]}")
fi
# Run server.
"${docker_run_base_cmd[@]}" --name "rhino-nvflare-localrun-server" -v "$tmpdir/poc/server:/home/localuser/server" -v "$abs_output_dir:/output" -v "$tmpdir/tb-logs/server:/tb-logs" --network rhino-nvflare-localrun --hostname rhino-nvflare-localrun-server "rhino-nvflare-localrun" server/startup/sub_start.sh rhino-nvflare-localrun-server >"$tmpdir/server_log.txt" 2>&1 &
# Wait for server to start.
echo "Waiting for FL server to start..."
while ! grep 'Server started' "$tmpdir/server_log.txt" >&/dev/null; do
  echo -n "."
  sleep 1;
done
echo ""
# Run clients.
for clientnum in $(seq 1 "$n_clients"); do
  "${docker_run_base_cmd[@]}" --name "rhino-nvflare-localrun-site-$clientnum" -v "$tmpdir/poc/site-$clientnum:/home/localuser/site-$clientnum" -v "$abs_input_dir:/input:ro" -v "$tmpdir/tb-logs/client-$clientnum:/tb-logs" --network rhino-nvflare-localrun "rhino-nvflare-localrun" site-$clientnum/startup/sub_start.sh "site-$clientnum" "$nvflare_server_connection_str" >"$tmpdir/site-${clientnum}_log.txt" 2>&1 &
done
echo "Server and $clientnum clients running."


mkdir "$tmpdir/poc/admin/transfer"
app_name="$(basename "$(pwd)")"
mkdir "$tmpdir/poc/admin/transfer/$app_name"
cp -r ./config "$tmpdir/poc/admin/transfer/$app_name"


if [ $auto -eq 1 ]; then

  stop_containers() {
    echo "Stopping server and client containers..."
    client_containers=()
    for clientnum in $(seq 1 $n_clients); do
      client_containers+=("rhino-nvflare-localrun-site-$clientnum")
    done
    set +e
    timeout 30 docker container stop -t 20 "rhino-nvflare-localrun-server" "${client_containers[@]}" >/dev/null
    if [ $? -eq 0 ]; then
      echo "Containers stopped."
    else
      echo "Stopping containers timed out after 30 seconds."
    fi
  }
  trap stop_containers EXIT

  echo "Running training automatically via the NVFlare Admin API."
  echo "To view server logs: less $tmpdir/server_log.txt"
  echo "To view client logs from client #1: less $tmpdir/site-1_log.txt"
  echo '(Tip: Type F (shift + f) in less to continuously read new data and scroll down.)'
  SCRIPTDIR="$( cd "$(dirname "$0")" && pwd )"
  docker run --rm -v "$SCRIPTDIR/drive_admin_api.py:/home/localuser/drive_admin_api.py" -v "$tmpdir/poc/admin:/home/localuser/admin" --workdir /home/localuser/admin --network rhino-nvflare-localrun "rhino-nvflare-localrun" python -u /home/localuser/drive_admin_api.py --host rhino-nvflare-localrun-server --port 8003 --num-clients "$n_clients" --timeout "$timeout_seconds" "$app_name"
  echo "App completed running successfully!"
  echo "Outputs should be found in: $output_dir"

else

  cat > "fl_admin.sh" << EOF
#!/bin/sh
exec docker run -it --rm -v "$tmpdir/poc/admin:/home/localuser/admin" --network rhino-nvflare-localrun "rhino-nvflare-localrun" admin/startup/fl_admin.sh rhino-nvflare-localrun-server
EOF
  chmod +x "fl_admin.sh"
  cat > "fl_terminate.sh" << EOF
#!/bin/sh
set -e
SCRIPTDIR="\$( cd "\$(dirname "\$0")" && pwd )"
echo "Stopping docker containers..."
docker container stop "rhino-nvflare-localrun-server" "rhino-nvflare-localrun-site-1" "rhino-nvflare-localrun-site-2" >/dev/null
rm "\$SCRIPTDIR/fl_admin.sh" "\$SCRIPTDIR/fl_terminate.sh"
echo "Local Rhino NVFlare network terminated."
EOF
  chmod +x "fl_terminate.sh"

  echo "Connect to the admin interface by running ./fl_admin.sh and entering "'"'"admin"'"'" for both the username and the password."
  echo "When done, stop the server and client by running ./fl_terminate.sh."

fi
