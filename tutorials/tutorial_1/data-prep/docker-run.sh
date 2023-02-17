#!/bin/bash
set -e

n_clients=1
timeout_seconds=600


function usage() {
  echo "Usage: $0 [OPTIONS] <input-dir> <output-dir>"
  echo
  echo "Available options:"
  echo "  --n-clients        Number of clients to run. (default: $n_clients)"
  echo "  --timeout-seconds  Maximum duration for application to run. (default: $timeout_seconds)"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi


while [[ "$1" == -* ]]; do
  case "$1" in
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
input_dir="$1"
output_dir="$2"

if [ -d "fl_admin.sh" ]; then
  echo "fl_admin.sh already exists; aborting"
  exit 1
fi
if [ -d "fl_terminate.sh" ]; then
  echo "fl_terminate.sh already exists; aborting"
  exit 1
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
sed -i.bak 's/"min_clients": [0-9]\+/"min_clients": '$n_clients'/' ./config/config_fed_server.json
set +e
DOCKER_BUILDKIT=1 docker build --build-arg="UID=$(id -u)" --build-arg="GID=$(id -g)" -t "rhino-nvflare-localrun" .
build_rc=$?
if [ $build_rc -ne 0 ]; then
  exit $build_rc
fi
set -e
mv ./config/config_fed_server.json.bak ./config/config_fed_server.json

tmpdir="$(mktemp -d)"
if [ ! -d $tmpdir ]; then
  echo "Failed to create temporary directory"
  exit 1
fi
echo "Created temporary directory: $tmpdir"


# temporary shim for unzip because NVFlare's poc.py requires it
cat > $tmpdir/unzip << EOF
#!/bin/sh
if [ "\$1" = "-q" ]; then
  shift
fi
echo "\$1"
echo "\$#"
if [ \$# -ne 1 ]; then
  echo "Error in unzip shim!"
  exit 1
fi
exec python -m zipfile -e "\$1" .
EOF
chmod +x $tmpdir/unzip
mkdir $tmpdir/poc
docker run --rm -v "$tmpdir/unzip:/home/localuser/bin/unzip" -v "$tmpdir/poc:/home/localuser/poc" --network none -u "$UID:$GID" "rhino-nvflare-localrun" /bin/sh -c 'echo y | PATH=/home/localuser/bin:$PATH poc -n '"$n_clients"' >/dev/null'
chmod +x "$tmpdir/poc/server/startup/sub_start.sh"
for clientnum in $(seq 1 $n_clients); do
  chmod +x "$tmpdir/poc/site-$clientnum/startup/sub_start.sh"
done
chmod +x "$tmpdir/poc/admin/startup/fl_admin.sh"
if [ 0 -eq $(docker network ls | tail -n +2 | awk '{ print $2 }' | grep '^rhino-nvflare-localrun$' | wc -l) ]; then
  docker network create rhino-nvflare-localrun
fi
docker run --rm --name "rhino-nvflare-localrun-server" -v "$tmpdir/poc/server:/home/localuser/server" -v "$abs_output_dir:/output" --network rhino-nvflare-localrun --hostname rhino-nvflare-localrun-server "rhino-nvflare-localrun" server/startup/sub_start.sh rhino-nvflare-localrun-server >"$tmpdir/server_log.txt" 2>&1 &
for clientnum in $(seq 1 $n_clients); do
  docker run --rm --name "rhino-nvflare-localrun-site-$clientnum" -v "$tmpdir/poc/site-$clientnum:/home/localuser/site-$clientnum" -v "$abs_input_dir:/input:ro" --network rhino-nvflare-localrun "rhino-nvflare-localrun" site-$clientnum/startup/sub_start.sh "site-$clientnum" rhino-nvflare-localrun-server >"$tmpdir/site-${clientnum}_log.txt" 2>&1 &
done
echo "Server and $clientnum clients running."

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

mkdir "$tmpdir/poc/admin/transfer"
app_name="$(basename $(pwd))"
mkdir "$tmpdir/poc/admin/transfer/$app_name"
cp -r ./config ./custom "$tmpdir/poc/admin/transfer/$app_name"

SCRIPTDIR="$( cd "$(dirname "$0")" && pwd )"
docker run --rm -v "$SCRIPTDIR/drive_admin_api.py:/home/localuser/drive_admin_api.py" -v "$tmpdir/poc/admin:/home/localuser/admin" --workdir /home/localuser/admin --network rhino-nvflare-localrun "rhino-nvflare-localrun" python -u /home/localuser/drive_admin_api.py --host rhino-nvflare-localrun-server --port 8003 --n-clients "$n_clients" --timeout "$timeout_seconds" "$app_name"
echo "App completed running successfully!"
echo "Outputs should be found in: $output_dir"
