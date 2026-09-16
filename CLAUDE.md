# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is `RhinoHealth/user-resources` - a curated collection of tutorials, examples, and utilities for the Rhino Federated Computing Platform (FCP). There is no application code, build step, or test suite; each subfolder is either a standalone runnable example/tutorial (a Dockerfile + config + a notebook or script) or a shared shell/Terraform utility. "Correctness" here means an example actually runs end-to-end against a real FCP workgroup and/or locally in Docker - there's no CI enforcing this, so treat working examples as fragile and verify changes by actually running them where feasible.

Four top-level areas, each with its own `README.md`:
- **`examples/`** - grab-and-go reference implementations organized by capability (`nvflare/`, `generalized-compute/`, `interactive-containers/`, `rhino-sdk/`, etc.), not narrated step-by-step.
- **`infrastructure/`** - OpenTofu (Terraform) modules (`AWS/`, `Azure/`, `GCP/`) for provisioning the on-prem client/workgroup connector.
- **`tutorials/`** - guided, step-by-step walkthroughs of FCP workflows, organized progressively (`0_Foundational/` then `1_Advanced/<topic>/`).
- **`utils/`** - shared shell scripts used across many examples (`docker-push.sh`, `gc-docker-run.sh`, `nvflare-docker-run.sh`, `upload-file-to-s3.sh`, etc.) - referenced from example directories as `../../../utils/<script>.sh`. Run any script with `-h`/`--help`.

## Commands

- **Build and push a container image** (from inside an example's directory): `../../../utils/docker-push.sh <workgroup-repo-name> <tag>` - builds and pushes in one step, and prints the resulting image URI (needed for `container_image_uri` in Code Object creation).
- **Test a Generalized Compute container locally**: `../../../utils/gc-docker-run.sh <input-dir> <output-dir>`.
- **Test an NVFlare container locally without a real FCP workgroup**: `nvflare simulator -w /tmp/nvflare-workspace -n <num_clients> -t <num_threads> .` run inside the built image. `utils/nvflare-docker-run.sh --auto` automates building + running this.
- **Committing notebooks**: a `nb-clean` pre-commit hook strips outputs and empty cells automatically - don't hand-strip them yourself, but expect committed `.ipynb` diffs to include only source changes.

## NVFlare-on-FCP: non-obvious constraints

These apply to any NVFlare example meant to run for real on FCP (not just via the local `nvflare simulator`), and were the source of most debugging time when building/fixing these examples - most are not documented anywhere else in this repo.

- **NVFlare version ceiling: pin `nvflare==2.6.0`.** FCP's server-side provisioning only has startup-kit templates up to NVFlare 2.6 (`CodeTypes.NVIDIA_FLARE_V2_6` is the newest value in the SDK). A container built with a newer NVFlare (e.g. 2.7+/2.8.x) fails with confusing, indirect errors from *inside* the deployed containers - a client error like `missing 'target' in server config ... provisioned with an older HA-based template`, or a server error like `Can't load class nvflare.app_common.logging.log_receiver.LogReceiver`. Both are symptoms of FCP generating a v2.6-era startup kit for a newer NVFlare that no longer matches it. This constraint doesn't apply to pure local Docker/simulator testing, which has no provisioning-template dependency.
- **`meta.json` + `app/` job-folder layout is required for NVFlare >= 2.4 on FCP.** The image needs a `meta.json` (with `deploy_map`/`min_clients`) at its container WORKDIR, and the actual `config/`/`custom/` folders nested under `app/` (i.e. `app/config/`, `app/custom/`), not at the container root. Without this, `start_training` fails with `Exception: Config file not found: meta.{json,conf,yml,yaml}` - FCP execs into the container looking for it and finds nothing. The local `nvflare simulator` doesn't require this, so a flat `config/`+`custom/` layout can silently "work" locally while being broken for real FCP runs.
- **Real training data lands at `/input/datasets/<dataset_uid>/file_data/...`, not a flat `/input/file_data/...`.** The flat path is a different (Generalized Compute / single-dataset) convention used by e.g. `infer.py`-style scripts, not by NVFlare FL client executors. An NVFlare client component should discover its dataset UID at runtime (e.g. `next(os.walk('/input/datasets'))[1][0]`) rather than hardcoding a path. Local Docker walkthroughs need to mount test data under a fake `datasets/<some-id>/file_data/...` subpath to exercise the same code path.
- **Two ways to give FCP a container image**: "auto-container" (FCP builds it from an uploaded folder, via the SDK's `folder_path` + `CodeExecutionMode.AUTO_CONTAINER_NVFLARE`), or a pre-built image you push yourself (`config={"container_image_uri": ...}` on `CodeObjectCreateInput`, no `code_execution_mode` needed). The latter is what `docker-push.sh` feeds into.
- **`create_code_object` defaults to silently reusing an existing Code Object by name.** `return_existing=True` is the default - re-running a creation cell after changing `config` (e.g. a new `container_image_uri`) will do nothing unless you pass `return_existing=False, add_version_if_exists=True` to force a new version.
- **`config_fed_client`/`config_fed_server` passed to `ModelTrainInput` are injected at runtime**, not baked into the image - changing NVFlare job config (round counts, etc.) doesn't require a rebuild. Actual code changes (`custom/*.py`) or `requirements.txt`/`meta.json`/`Dockerfile` changes do.
- **Runtime secrets convention**: `secrets_fed_client`/`secrets_fed_server` passed to `ModelTrainInput` land inside the running containers at `/input/secret_run_params.json` (client) and `/server-credentials/secret_run_params.json` (server) respectively, as `{"key": "..."}` JSON.

## Formatting
- Even though the repo itself is called "Rhino Health", the term "Rhino Health" is now effectively deprecated post-rebranding.
    - Mentions of "Rhino Health" in any text or comments should be replaced with "Rhino Federated Computing Platform (FCP)".
    - The old docs.rhinohealth.com site has been deprecated, and should be replaced with[RhinoDocs](https://docs.rhinofcp.com/)
    - The old support@rhinohealth.com email has been deprecated, and should be replaced with [support@rhinofcp.com](mailto:support@rhinofcp.com)
- Every folder should have a README.md with sufficient detail to understand and execute any contents.
    - These should generally contain sections such as Description, Resources (an alphebetized table of contents, with folders preceding any files), Pre-requisites / How to Execute / Instructions (if applicable), Troubleshooting (if applicable), and Getting Help
    - Update relevant READMEs upon file updates to make sure it always remains up to date.
- This is a public-facing repo that should not contain any proprietary or sensitive information. When in doubt, prompt the user for permission before including something. Always err on the side of caution.
- Ensure dummy/test datasets are included, if referenced, and note why this data can be shared (e.g., data is synthetic and all PHI is fake)
- Assume audience is not always technical & elaborate on details where possible
- Note if there are any edge cases to be aware of
- Include hyperlinks to other sections as relevant
- Include .gitignore if necessary