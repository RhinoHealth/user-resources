#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: $0 <model-weights-file>"
  exit 1
fi

model_weights_file="$1"

if [ ! -f "$model_weights_file" ]; then
  >&2 echo "Model weights file $model_weights_file does not exist."
  exit 1
fi

for script_path in "./infer.sh" "./infer.py"; do
  if [ -f "$script_path" ]; then
    if [ ! -x "$script_path" ]; then
      >&2 echo "$script_path must be executable"
      exit 1
    fi
    exec "$script_path" "$model_weights_file"
  fi
done

>&2 echo "Inference script (infer.sh or infer.py) not found."
exit 1
