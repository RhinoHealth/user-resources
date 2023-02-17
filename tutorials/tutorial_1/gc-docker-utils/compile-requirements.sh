#!/bin/bash

function usage() {
  echo "Usage: $0 [filename.in]"
}

if [ $# -gt 1 ]; then
  usage
  exit 0
fi

input_file="${1:-requirements.in}"
output_file="${input_file%.in}.txt"

if command -v pip-compile &> /dev/null; then
  exec pip-compile --upgrade --build-isolation --output-file "$output_file" "$input_file"
elif command -v pipx &> /dev/null; then
  exec pipx run --spec pip-tools pip-compile --upgrade --build-isolation --output-file "$output_file" "$input_file"
fi

echo "Must have either the pip-compile (from pip-tools) or pipx commands available."
echo "We recommend installing pipx globally: python3 -m pip install --user pipx"
echo "See the pipx documentation for details: https://pypa.github.io/pipx/"
exit 1
