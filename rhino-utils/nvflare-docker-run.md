# NVFlare Local Training Simulation

This script simulates how the Rhino FCP platform runs your NVFlare training job, allowing you to test and debug your containerized app locally before deploying to the platform.

## Prerequisites

- Docker
- **macOS only:** GNU coreutils (`brew install coreutils`)

## Installation (Recommended)

Copy both scripts to `/usr/local/bin/`, dropping the `.sh` extension from the main script, and make it executable:

```bash
cp nvflare-docker-run.sh /usr/local/bin/nvflare-docker-run
cp drive_admin_api.py /usr/local/bin/drive_admin_api.py
chmod +x /usr/local/bin/nvflare-docker-run
```

You may need `sudo` depending on your system permissions:

```bash
sudo cp nvflare-docker-run.sh /usr/local/bin/nvflare-docker-run
sudo cp drive_admin_api.py /usr/local/bin/drive_admin_api.py
sudo chmod +x /usr/local/bin/nvflare-docker-run
```

Verify that `/usr/local/bin/` is in your PATH:

```bash
echo $PATH
```

You should see `/usr/local/bin` in the output. If not, add it to your shell profile (e.g. `~/.bashrc` or `~/.zshrc`):

```bash
# For zsh (default on macOS):
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash (default on Ubuntu):
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify the script is installed and executable:

```bash
which nvflare-docker-run
```

This should return `/usr/local/bin/nvflare-docker-run`.

Alternatively, if you prefer to keep the files in your project directory, you can run the script directly without installation:

```bash
./nvflare-docker-run.sh [OPTIONS] <input-dir> <output-dir>
```

## Directory Structure

### Project Directory
Your project should be structured as follows (see [this example](https://github.com/RhinoHealth/user-resources/tree/main/tutorials/tutorial_1/containers/prediction-model) for reference):
```
<project-dir>/
  Dockerfile
  requirements.txt
  meta.json
  app/
    config/
      config_fed_server.json
      config_fed_client.json
    custom/
      <your training code>
```

### Input Directory
The input directory must mirror how datasets are mounted on the platform, with a subdirectory for each client:
```
<input-dir>/
  site-1/
    <dataset-uid>/
      dataset.csv
  site-2/
    <dataset-uid>/
      dataset.csv
```

Each `site-n/` directory represents one client's data. Within each site, you can have one or more dataset subdirectories — the directory name can be anything, as it represents the dataset UID assigned by the platform. Each dataset subdirectory must contain a `dataset.csv` file.

### Output Directory
Training outputs will be written to:
```
<output-dir>/
  model_parameters.pt    (or model_parameters/ for multiple files)
  logs/
    server_log.txt
    site-1_log.txt
    site-2_log.txt
    ...
```

## Usage

```bash
nvflare-docker-run [OPTIONS] <input-dir> <output-dir>
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-f FILE` | Dockerfile to use for building the container image | `./Dockerfile` |
| `--platform PLATFORM` | Platform to build container for, e.g. `linux/amd64` | `linux/amd64` |
| `--progress STYLE` | Docker build output style: `auto` or `plain` | `auto` |
| `--n-clients NUM` | Number of clients to run | `1` |
| `--app_name NAME` | Name of the NVFlare app directory | `app` |
| `--timeout-seconds NUM` | Maximum duration for the training run in seconds | `600` |
| `--manual` | Manually drive the training via the admin shell | off |
| `--gpus GPUS` | GPUs to make available to all containers | none |

## Running a Training Job

### Auto Mode (default)

Auto mode is the recommended way to run a training job. The script will automatically submit the job, wait for completion, and stop all containers when done.

From your project directory:
```bash
nvflare-docker-run --n-clients 2 <input-dir> <output-dir>
```

If your Dockerfile is in a different directory:
```bash
nvflare-docker-run -f <path-to-dockerfile> --n-clients 2 <input-dir> <output-dir>
```

Once running, log paths will be printed to the terminal:
```
Server logs can be found here: <output-dir>/logs/server_log.txt
Client logs from client #1 can be found here: <output-dir>/logs/site-1_log.txt
...
```

To monitor logs in real time from a separate terminal:
```bash
less +F <output-dir>/logs/server_log.txt
```

When training completes, outputs will be found in `<output-dir>`.

### Manual Mode

Manual mode gives you direct access to the NVFlare admin shell, which is useful for debugging or stepping through the training process interactively.

```bash
nvflare-docker-run --manual --n-clients 2 <input-dir> <output-dir>
```

Once the server and clients are running, two helper scripts will be created in your current directory: `fl_admin.sh` and `fl_terminate.sh`.

**1. Connect to the admin shell:**
```bash
./fl_admin.sh
```
When prompted, enter `admin@nvidia.com` for the username and `admin` for the password.

**2. Submit and start the job:**
```
> submit_job job
```

**3. Monitor progress:**
```
> check_status server
> check_status client
```

**4. When training is complete, shut down gracefully — always shut down clients before the server:**
```
> shutdown client
> shutdown server
> bye
```

**5. Clean up containers and helper scripts:**
```bash
./fl_terminate.sh
```

## Troubleshooting

**`No NVFlare config directory found`**
The script couldn't find your app's config directory. Make sure your config is at `app/config/` relative to your project directory, or specify a different app name with `--app_name`.

**`fl_admin.sh already exists; aborting`**
A previous manual mode session was not cleaned up. Run `./fl_terminate.sh` if containers are still running, or delete `fl_admin.sh` and `fl_terminate.sh` manually.

**`Input directory validation failed`**
Your input directory is not structured correctly. See the [Input Directory](#input-directory) section above for the required structure.

**`Only versions 2.0, 2.2, 2.3, 2.4, 2.5, 2.6 and 2.7 of NVFLARE are supported`**
The version of NVFlare installed in your container is not supported. Make sure your `requirements.txt` specifies a supported version.

**Training times out**
Increase the timeout with `--timeout-seconds`. The default is 600 seconds (10 minutes).