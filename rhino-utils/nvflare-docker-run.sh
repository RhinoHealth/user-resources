#!/bin/bash
set -eu -o pipefail


function usage() {
  echo "Run a local NVFlare training job to test your containerized NVFlare app."
  echo
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


#####################
# Argument parsing. #
#####################

docker_build_args=()
build_platform="linux/amd64"
docker_run_args=()
n_clients=1
timeout_seconds=600
auto=0
app_name="$(basename "$(pwd)")"

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
  --n-clients=*)
    n_clients="${1#--n-clients=}"
    ;;
  --timeout-seconds)
    shift
    [ $# -eq 0 ] && usage && exit 1
    timeout_seconds="$1"
    ;;
  --timeout-seconds=*)
    timeout_seconds="${1#--timeout-seconds=}"
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
  --app_name)
    shift
    [ $# -eq 0 ] && usage && exit 1
    app_name="$1"
    ;;
  --app_name=*)
    app_name="${1#--app_name=}"
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


#############################################
# Check for existing files and directories. #
#############################################

# In non-auto mode, bail if fl_admin.sh or fl_terminate.sh already exist.
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

# The input directory must exist.
if [ ! -d "$input_dir" ]; then
  echo "No such directory: $input_dir"
  exit 1
fi
abs_input_dir="$(cd "$input_dir" && pwd -P)"

# Create the output directory if it doesn't exist.
[ -d "$output_dir" ] || mkdir "$output_dir"
abs_output_dir="$(cd "$output_dir" && pwd -P)"

# Find NVFlare config directory.
if [ -d "./$app_name/config" ]; then
  config_dir="$app_name/config"
elif [ -d ./config ]; then
  config_dir="config"
else
  echo "No NVFlare config directory found."
  exit 1
fi


##############################
# Build the container image. #
##############################

# Before building. override min_clients in config_fed_server.json.
if [ -e ./$config_dir/config_fed_server.json.bak ]; then
  mv ./$config_dir/config_fed_server.json.bak ./$config_dir/config_fed_server.json
fi
sed -i.bak 's/"min_clients"[[:space:]]*:[[:space:]]*[0-9][0-9]*/"min_clients": '$n_clients'/' ./$config_dir/config_fed_server.json
docker_build_base_cmd=(docker build)
if [ ${#docker_build_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${docker_build_args[@]}")
fi
uid=$(id -u)
gid=$(id -g)
set -x
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --build-arg="UID=$uid" --build-arg="GID=$gid" -t "rhino-nvflare-localrun" .
{ set +x; } 2>/dev/null
mv ./$config_dir/config_fed_server.json.bak ./$config_dir/config_fed_server.json


####################################################
# Create temporary working directory for this run. #
####################################################

tmpdir="$(mktemp -d)"
if [ ! -d $tmpdir ]; then
  echo "Failed to create temporary directory"
  exit 1
fi
echo "Created temporary directory: $tmpdir"


#######################################
# Detect the version of NVFlare used. #
#######################################

nvflare_version="$(docker run --rm --network none "rhino-nvflare-localrun" pip freeze | grep '^nvflare==' | cut -d= -f3)"
IFS='.' read -r -a nvflare_version_parts <<< "$nvflare_version"


###########################################
# Run NVFlare provisioning in "poc" mode. #
###########################################

# Create a shim for unzip: NVFlare's poc.py requires it but it isn't necessarily available in the container.
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

# Create a wrapper script for running NVFlare's poc tool.
# Note that unlike other time the container is run in this script,
# in this case it will be run as root to enable patching NVFlare.
cat > $tmpdir/prep_poc.sh << EOF
#!/bin/sh
set -e

if [ "${nvflare_version_parts[1]}" -eq 0 ]; then
  echo y | runuser -u localuser -- poc -n "$n_clients" >/dev/null
elif [ "${nvflare_version_parts[1]}" -eq 2 ] || [ "${nvflare_version_parts[1]}" -eq 3 ]; then
  export NVFLARE_POC_WORKSPACE=/tmp/nvflare/poc
  echo y | runuser -u localuser -- nvflare poc --prepare -n "$n_clients" >/dev/null
  mv /tmp/nvflare/poc/* poc/
elif [ "${nvflare_version_parts[1]}" -eq 4 ] || [ "${nvflare_version_parts[1]}" -eq 5 ]; then
  # Override the host name used for the server in poc mode in NVFlare's local_cert.py.
  nvflare_src_dir="\$(python -c 'import nvflare, os; print(os.path.dirname(nvflare.__file__))')"
  sed 's/"localhost"/"rhino-nvflare-localrun-server"/' "\$nvflare_src_dir"/lighter/impl/local_cert.py > /tmp/local_cert.py
  mv /tmp/local_cert.py "\$nvflare_src_dir"/lighter/impl/local_cert.py
  export NVFLARE_POC_WORKSPACE=/tmp/nvflare/poc
  echo y | runuser -u localuser -- nvflare poc prepare -n "$n_clients" >/dev/null
  mv /tmp/nvflare/poc/* poc/
else
  echo >&2 "Only versions 2.0, 2.2, 2.3, 2.4 and 2.5 of NVFLARE are supported."
  exit 1
fi
EOF
chmod +x $tmpdir/prep_poc.sh

# Run poc preparation in the container, as root (see explanation above).
mkdir $tmpdir/poc
if ! docker run --rm -v "$tmpdir/unzip:/home/localuser/bin/unzip" -v "$tmpdir/prep_poc.sh:/home/localuser/bin/prep_poc.sh" -v "$tmpdir/poc:/home/localuser/poc" --network none -u0:0 "rhino-nvflare-localrun" /bin/sh -c 'PATH=/home/localuser/bin:$PATH prep_poc.sh '"$n_clients"; then
  rc=$?
  echo 'Running NVFlARE'"'"'s poc script failed.'
  echo 'Make sure NVFLARE is installed in the container,'
  echo 'and that the `poc` executable is available on $PATH in the container.'
  exit $rc
fi
if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
  poc_dir="$tmpdir/poc/example_project/prod_00"
  poc_admin_dir="$poc_dir/admin@nvidia.com"
else
  poc_dir="$tmpdir/poc"
  poc_admin_dir="$poc_dir/admin"
fi


#############################
# Post-provisioning tweaks. #
#############################

# Make the generated sub_start.sh files executable, since they will be invoked directly.
chmod +x "$poc_dir/server/startup/sub_start.sh"
for clientnum in $(seq 1 "$n_clients"); do
  chmod +x "$poc_dir/site-$clientnum/startup/sub_start.sh"
done
# Ensure fl_admin.sh is executable.
chmod +x "$poc_admin_dir/startup/fl_admin.sh"
# Override the host name used for the server in poc mode in NVFlare's local_cert.py.
if [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]] || [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
  find "$poc_dir/" -type f -name 'fed_*.json' \
    -exec sed -i.bak 's/localhost:8002/rhino-nvflare-localrun-server:8002/' {} \; \
    -exec rm {}.bak \;
  find "$poc_dir/" -type f -name 'fed_server.json' \
    -exec sed -i.bak 's/"localhost"/"rhino-nvflare-localrun-server"/' {} \; \
    -exec rm {}.bak \;
  if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
    # Re-sign the files after having edited the config files.
    python_sign_configs_script="import json
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from nvflare.lighter.utils import sign_all

base_path = Path('/home/localuser/poc/example_project')
cert = json.loads((base_path / 'state' / 'cert.json').read_text())
serialized_root_pri_key = cert['root_pri_key'].encode('ascii')
root_pri_key = serialization.load_pem_private_key(serialized_root_pri_key, password=None, backend=default_backend())

for startup_dir in base_path.glob('**/startup'):
    signatures = sign_all(str(startup_dir), root_pri_key)
    (startup_dir / 'signature.json').write_text(json.dumps(signatures))
"
    if ! docker run --rm -v "$tmpdir/poc:/home/localuser/poc" --network none "rhino-nvflare-localrun" python -c "$python_sign_configs_script"; then
      rc=$?
      echo 'Running config signing script failed.'
      exit $rc
    fi
  fi
fi


#####################################
# Run NVFlare server and client(s). #
#####################################

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
"${docker_run_base_cmd[@]}" --name "rhino-nvflare-localrun-server" -v "$poc_dir/server:/home/localuser/server" -v "$abs_output_dir:/output" -v "$tmpdir/tb-logs/server:/tb-logs" --network rhino-nvflare-localrun --hostname rhino-nvflare-localrun-server "rhino-nvflare-localrun" server/startup/sub_start.sh rhino-nvflare-localrun-server >"$tmpdir/server_log.txt" 2>&1 &

# Wait for server to start.
echo "Waiting for FL server to start..."
while ! grep 'Server started' "$tmpdir/server_log.txt" >&/dev/null; do
  echo -n "."
  sleep 1;
done
echo ""

# Run clients.
if [[ "$nvflare_version" == 2.0.* ]]; then
  nvflare_server_connection_str="rhino-nvflare-localrun-server"
elif [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]] || [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
  nvflare_server_connection_str="rhino-nvflare-localrun-server:8002:8002"
else
  echo >&2 "Only versions 2.0, 2.2, 2.3, 2.4 and 2.5 of NVFLARE are supported."
  exit 1
fi
for clientnum in $(seq 1 "$n_clients"); do
  "${docker_run_base_cmd[@]}" --name "rhino-nvflare-localrun-site-$clientnum" -v "$poc_dir/site-$clientnum:/home/localuser/site-$clientnum" -v "$abs_input_dir:/input:ro" -v "$tmpdir/tb-logs/client-$clientnum:/tb-logs" --network rhino-nvflare-localrun "rhino-nvflare-localrun" site-$clientnum/startup/sub_start.sh "site-$clientnum" "$nvflare_server_connection_str" >"$tmpdir/site-${clientnum}_log.txt" 2>&1 &
done

echo "Server and $clientnum clients running."


#####################################
# Prepare to start the NVFlare app. #
#####################################

if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
  app_dir="job/$app_name"
else
  app_dir="$app_name"
fi
mkdir -p "$poc_admin_dir/transfer/$app_dir"
if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
  cp ./meta.* "$poc_admin_dir/transfer/job/"
fi
cp -r ./"$config_dir" "$poc_admin_dir/transfer/$app_dir/config"


########################
# Auto or manual mode? #
########################

if [ $auto -eq 1 ]; then

  # Set a trap to stop the containers when the script exits.
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

  # Run the app and wait for its completion via drive_admin_api.py.
  echo "Running training automatically via the NVFlare Admin API."
  echo "To view server logs: less $tmpdir/server_log.txt"
  echo "To view client logs from client #1: less $tmpdir/site-1_log.txt"
  echo '(Tip: Type F (shift + f) in less to continuously read new data and scroll down.)'
  SCRIPTDIR="$( cd "$(dirname "$0")" && pwd )"
  docker run --rm -v "$SCRIPTDIR/drive_admin_api.py:/home/localuser/drive_admin_api.py" -v "$poc_admin_dir:/home/localuser/admin" --workdir /home/localuser/admin --network rhino-nvflare-localrun "rhino-nvflare-localrun" python -u /home/localuser/drive_admin_api.py --host rhino-nvflare-localrun-server --port 8003 --num-clients "$n_clients" --timeout "$timeout_seconds" "$app_name"
  echo "App completed running successfully!"
  echo "Outputs should be found in: $output_dir"

else

  # Create fl_admin.sh and fl_terminate.sh scripts.
  cat > "fl_admin.sh" << EOF
#!/bin/sh
exec docker run -it --rm -v "$poc_admin_dir:/home/localuser/admin" --network rhino-nvflare-localrun "rhino-nvflare-localrun" admin/startup/fl_admin.sh rhino-nvflare-localrun-server
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

  # Print instructions for manual mode.
  if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]]; then
    echo "Connect to the admin interface by running ./fl_admin.sh and"
    echo "entering "'"'"admin@nvidia.com"'"'" for the username and "'"'"admin"'"'" for the password."
  else
    echo "Connect to the admin interface by running ./fl_admin.sh and"
    echo "entering "'"'"admin"'"'" for both the username and the password."
  fi
  echo "When done, stop the server and client by running ./fl_terminate.sh."

fi
