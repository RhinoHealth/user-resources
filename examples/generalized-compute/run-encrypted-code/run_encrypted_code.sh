#!/bin/bash

if [ $# -ne 1 ]; then
  >&2 echo "Usage: $0 encrypted_file_path"
  exit 1
fi

ENCRYPTED_FILE_PATH=$1
DECRYPTED_FILE_PATH=${ENCRYPTED_FILE_PATH}.py

DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")

PYTHONUNBUFFERED=1

# Wait a bit so that k8s will recognize that the container has started running successfully.
sleep 2

set -x
set -e

# Decrypt the code
python $DIR/decrypt_code.py ${ENCRYPTED_FILE_PATH} ${DECRYPTED_FILE_PATH}

# Run the decrypted code
python ${DECRYPTED_FILE_PATH}

