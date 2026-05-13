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
  echo " --app_name NAME        Name of the NVFlare app directory. (default: app)"
  echo " --timeout-seconds NUM  Maximum duration for application to run. (default: $timeout_seconds)"
  echo " --manual               Manually drive the training via the admin shell"
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
auto=1
dockerfile_dir=""
app_name="app"

while [[ $# -ne 0 ]] && [[ "$1" == -* ]]; do
  case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
  -f)
    shift
    [ $# -eq 0 ] && usage && exit 1
    dockerfile_path="$(cd "$(dirname "$1")" && pwd -P)/$(basename "$1")"
    docker_build_args=("-f" "$dockerfile_path")
    dockerfile_dir="$(dirname "$dockerfile_path")"
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
  --manual)
    auto=0
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

# Validate per-client input directory structure.
input_errors=()
for clientnum in $(seq 1 "$n_clients"); do
  site_dir="$abs_input_dir/site-$clientnum"
  if [ ! -d "$site_dir" ]; then
    input_errors+=("  site-$clientnum: missing directory $site_dir")
    continue
  fi
  # Check that at least one dataset subdirectory exists.
  dataset_dirs=("$site_dir"/*)
  if [ ! -d "${dataset_dirs[0]}" ]; then
    input_errors+=("  site-$clientnum: no dataset subdirectories found in $site_dir")
    continue
  fi
  # Check that each dataset subdirectory contains a dataset.csv.
  for dataset_dir in "$site_dir"/*/; do
    if [ ! -f "$dataset_dir/dataset.csv" ]; then
      input_errors+=("  site-$clientnum: missing dataset.csv in $dataset_dir")
    fi
  done
done
if [ ${#input_errors[@]} -gt 0 ]; then
  echo "Input directory validation failed:"
  for error in "${input_errors[@]}"; do
    echo "$error"
  done
  echo ""
  echo "Expected structure:"
  echo "  <input-dir>/"
  echo "    site-1/"
  echo "      <dataset-uid>/"
  echo "        dataset.csv"
  echo "    site-2/"
  echo "      ..."
  exit 1
fi

# Create the output directory if it doesn't exist.
[ -d "$output_dir" ] || mkdir "$output_dir"
abs_output_dir="$(cd "$output_dir" && pwd -P)"

# Establish project directory - where the Dockerfile and app files live.
if [ -n "$dockerfile_dir" ]; then
  project_dir="$dockerfile_dir"
else
  project_dir="$(pwd)"
fi

# Find NVFlare config directory.
if [ -d "$project_dir/$app_name/config" ]; then
  config_dir="$app_name/config"
elif [ -d "$project_dir/config" ]; then
  config_dir="config"
else
  echo "No NVFlare config directory found."
  exit 1
fi


##############################
# Build the container image. #
##############################

# Before building, override min_clients and num_clients in config_fed_server.json.
if [ -e "$project_dir/$config_dir/config_fed_server.json.bak" ]; then
  mv "$project_dir/$config_dir/config_fed_server.json.bak" "$project_dir/$config_dir/config_fed_server.json"
fi
sed -i.bak \
  -e 's/"min_clients"[[:space:]]*:[[:space:]]*[0-9][0-9]*/"min_clients": '$n_clients'/' \
  -e 's/"num_clients"[[:space:]]*:[[:space:]]*[0-9][0-9]*/"num_clients": '$n_clients'/' \
  "$project_dir/$config_dir/config_fed_server.json"

# Patch min_clients in meta.json if it exists.
if [ -f "$project_dir/meta.json" ]; then
  sed -i.bak 's/"min_clients"[[:space:]]*:[[:space:]]*[0-9][0-9]*/"min_clients": '$n_clients'/' "$project_dir/meta.json"
fi

docker_build_base_cmd=(docker build)
if [ ${#docker_build_args[@]} -gt 0 ]; then
  docker_build_base_cmd+=("${docker_build_args[@]}")
fi
uid=$(id -u)
gid=$(id -g)
set -x
build_context="."
if [ -n "$dockerfile_dir" ]; then
  build_context="$dockerfile_dir"
fi
DOCKER_BUILDKIT=1 "${docker_build_base_cmd[@]}" --build-arg="UID=$uid" --build-arg="GID=$gid" -t "rhino-nvflare-localrun" "$build_context"
{ set +x; } 2>/dev/null


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
# Note that unlike other times the container is run in this script,
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
  nvflare_src_dir="\$(python -c 'import nvflare, os; print(os.path.dirname(nvflare.__file__))')"
  sed 's/"localhost"/"rhino-nvflare-localrun-server"/' "\$nvflare_src_dir"/lighter/impl/local_cert.py > /tmp/local_cert.py
  mv /tmp/local_cert.py "\$nvflare_src_dir"/lighter/impl/local_cert.py
  export NVFLARE_POC_WORKSPACE=/tmp/nvflare/poc
  echo y | runuser -u localuser -- nvflare poc prepare -n "$n_clients" >/dev/null
  mv /tmp/nvflare/poc/* poc/
elif [ "${nvflare_version_parts[1]}" -eq 6 ] || [ "${nvflare_version_parts[1]}" -eq 7 ]; then
  nvflare_src_dir="\$(python -c 'import nvflare, os; print(os.path.dirname(nvflare.__file__))')"
  sed 's/update_server_default_host(project_config, "localhost")/update_server_default_host(project_config, "rhino-nvflare-localrun-server")/' "\$nvflare_src_dir"/tool/poc/poc_commands.py > /tmp/poc_commands.py
  mv /tmp/poc_commands.py "\$nvflare_src_dir"/tool/poc/poc_commands.py
  export NVFLARE_POC_WORKSPACE=/tmp/nvflare/poc
  echo y | runuser -u localuser -- nvflare poc prepare -n "$n_clients" >/dev/null
  mv /tmp/nvflare/poc/* poc/
else
  echo >&2 "Only versions 2.0, 2.2, 2.3, 2.4, 2.5, 2.6 and 2.7 of NVFLARE are supported."
  exit 1
fi
EOF
chmod +x $tmpdir/prep_poc.sh

# Run poc preparation in the container, as root (see explanation above).
mkdir $tmpdir/poc
if ! docker run --rm -v "$tmpdir/unzip:/home/localuser/bin/unzip" -v "$tmpdir/prep_poc.sh:/home/localuser/bin/prep_poc.sh" -v "$tmpdir/poc:/home/localuser/poc" --network none -u0:0 "rhino-nvflare-localrun" /bin/sh -c 'PATH=/home/localuser/bin:$PATH prep_poc.sh '"$n_clients" >/dev/null; then
  rc=$?
  echo 'Running NVFlARE'"'"'s poc script failed.'
  echo 'Make sure NVFLARE is installed in the container,'
  echo 'and that the `poc` executable is available on $PATH in the container.'
  exit $rc
fi
if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
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
# Override the host name used for the server in poc mode.
if [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]] || [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
  find "$poc_dir/" -type f -name 'fed_*.json' \
    -exec sed -i.bak 's/localhost:8002/rhino-nvflare-localrun-server:8002/' {} \; \
    -exec rm {}.bak \;
  find "$poc_dir/" -type f -name 'fed_server.json' \
    -exec sed -i.bak 's/"localhost"/"rhino-nvflare-localrun-server"/' {} \; \
    -exec rm {}.bak \;
  if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
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
    if ! docker run --rm -v "$tmpdir/poc:/home/localuser/poc" --network none "rhino-nvflare-localrun" python -c "$python_sign_configs_script" >/dev/null; then
      rc=$?
      echo 'Running config signing script failed.'
      exit $rc
    fi
  fi
fi


#####################################
# Run NVFlare server and client(s). #
#####################################

STDBUF=$(command -v gstdbuf || command -v stdbuf || echo "")
if [ -n "$STDBUF" ]; then
  TEE_CMD="$STDBUF -oL tee"
else
  TEE_CMD="tee"
fi

if ! docker network ls | tail -n +2 | awk '{ print $2 }' | grep -q '^rhino-nvflare-localrun$'; then
  docker network create --internal rhino-nvflare-localrun
fi

mkdir -p "$abs_output_dir/logs"
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
"${docker_run_base_cmd[@]}" -t --name "rhino-nvflare-localrun-server" -v "$poc_dir/server:/home/localuser/server" -v "$abs_output_dir:/output" -v "$tmpdir/tb-logs/server:/tb-logs" --network rhino-nvflare-localrun --hostname rhino-nvflare-localrun-server "rhino-nvflare-localrun" server/startup/sub_start.sh rhino-nvflare-localrun-server 2>&1 | $TEE_CMD "$tmpdir/server_log.txt" "$abs_output_dir/logs/server_log.txt" > /dev/null &

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
elif [[ "$nvflare_version" == 2.2.* ]] || [[ "$nvflare_version" == 2.3.* ]] || [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
  nvflare_server_connection_str="rhino-nvflare-localrun-server:8002:8002"
else
  echo >&2 "Only versions 2.0, 2.2, 2.3, 2.4, 2.5, 2.6 and 2.7 of NVFLARE are supported."
  exit 1
fi
for clientnum in $(seq 1 "$n_clients"); do
  "${docker_run_base_cmd[@]}" -t --name "rhino-nvflare-localrun-site-$clientnum" -v "$poc_dir/site-$clientnum:/home/localuser/site-$clientnum" -v "$abs_input_dir/site-$clientnum:/input/datasets:ro" -v "$tmpdir/tb-logs/client-$clientnum:/tb-logs" --network rhino-nvflare-localrun "rhino-nvflare-localrun" site-$clientnum/startup/sub_start.sh "site-$clientnum" "$nvflare_server_connection_str" 2>&1 | $TEE_CMD "$tmpdir/site-${clientnum}_log.txt" "$abs_output_dir/logs/site-${clientnum}_log.txt" > /dev/null &
done

echo "Server and $n_clients clients running."


#####################################
# Prepare to start the NVFlare app. #
#####################################

if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
  app_dir="job/$app_name"
else
  app_dir="$app_name"
fi
mkdir -p "$poc_admin_dir/transfer/$app_dir"
if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
  cp "$project_dir"/meta.* "$poc_admin_dir/transfer/job/"
fi
if [ -f "$project_dir/meta.json.bak" ]; then
  mv "$project_dir/meta.json.bak" "$project_dir/meta.json"
fi
cp -r "$project_dir/$config_dir" "$poc_admin_dir/transfer/$app_dir/config"
mv "$project_dir/$config_dir/config_fed_server.json.bak" "$project_dir/$config_dir/config_fed_server.json"


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
  echo "Server logs can be found here: $abs_output_dir/logs/server_log.txt"
  for clientnum in $(seq 1 "$n_clients"); do
    echo "Client logs from client #$clientnum can be found here: $abs_output_dir/logs/site-${clientnum}_log.txt"
  done
  echo '(Tip: Use `less <log_path>` in terminal. Once logs appear, type F (shift + f) to continuously read new data and scroll down.)'
  SCRIPTDIR="$( cd "$(dirname "$0")" && pwd )"
  cp "$SCRIPTDIR/drive_admin_api.py" "$tmpdir/drive_admin_api.py"
  docker run --rm -v "$tmpdir/drive_admin_api.py:/home/localuser/drive_admin_api.py" -v "$poc_admin_dir:/home/localuser/admin" --workdir /home/localuser/admin --network rhino-nvflare-localrun --entrypoint= "rhino-nvflare-localrun" python -u /home/localuser/drive_admin_api.py --host rhino-nvflare-localrun-server --port 8003 --num-clients "$n_clients" --timeout "$timeout_seconds" "$app_name"
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
SCRIPTDIR="\$( cd "\$(dirname "\$0")" && pwd )"
echo "Stopping docker containers..."
client_containers=""
for clientnum in \$(seq 1 $n_clients); do
  client_containers="\$client_containers rhino-nvflare-localrun-site-\$clientnum"
done
docker container stop "rhino-nvflare-localrun-server" \$client_containers >/dev/null 2>&1 || true
rm "\$SCRIPTDIR/fl_admin.sh" "\$SCRIPTDIR/fl_terminate.sh"
echo "Local Rhino NVFlare network terminated."
EOF
  chmod +x "fl_terminate.sh"

  # Print instructions for manual mode.
  if [[ "$nvflare_version" == 2.4.* ]] || [[ "$nvflare_version" == 2.5.* ]] || [[ "$nvflare_version" == 2.6.* ]] || [[ "$nvflare_version" == 2.7.* ]]; then
    echo "Connect to the admin interface by running ./fl_admin.sh and"
    echo "entering "'"'"admin@nvidia.com"'"'" for the username and "'"'"admin"'"'" for the password."
  else
    echo "Connect to the admin interface by running ./fl_admin.sh and"
    echo "entering "'"'"admin"'"'" for both the username and the password."
  fi
  echo "When done, stop the server and client by running ./fl_terminate.sh."

fi
