#!/usr/bin/env bash
set -eu -o pipefail

set +x
models_dir="$(python -c '
import json
import os

try:
    with open("/input/run_params.json", encoding="utf-8") as f:
        run_params = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    run_params = {}
models_dir = run_params.get("OLLAMA_MODELS")
if models_dir:
    print(models_dir)
')"
if [[ -n "$models_dir" ]]; then
  OLLAMA_MODELS="$models_dir"
  export OLLAMA_MODELS
fi

exec /usr/local/bin/ollama serve
