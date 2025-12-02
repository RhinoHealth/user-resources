#!/usr/bin/env python
import argparse
import json
import logging
import sys
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypt a file using a key from the GC run parameters")
    parser.add_argument("input_filename", help="input filename")
    parser.add_argument("output_filename", help="output filename")
    args = parser.parse_args()

    # Check input file exists
    if not Path(args.input_filename).exists():
        print(f"File not found: {args.input_filename}", file=sys.stderr)
        sys.exit(1)

    # Find and validate secret_run_params.json
    if Path("/server-credentials").exists():
        secret_run_params_file_path = Path("/server-credentials/secret_run_params.json")
    elif Path("/input").exists():
        secret_run_params_file_path = Path("/input/secret_run_params.json")
    else:
        print("Could not find directory for secret_run_params.json!", file=sys.stderr)
        sys.exit(1)

    if not secret_run_params_file_path.is_file():
        print("secret_run_params.json file is missing.", file=sys.stderr)
        sys.exit(1)

    # Load and parse secret_run_params.json
    with secret_run_params_file_path.open("rb") as secret_run_params_file:
        try:
            secret_run_params = json.load(secret_run_params_file)
        except json.JSONDecodeError as exc:
            print(f"Error decoding JSON in secret_run_params.json: {str(exc)}", file=sys.stderr)
            sys.exit(1)

    # Get private key from params
    try:
        private_key = RSA.import_key(secret_run_params["decrypt_key"])
    except KeyError:
        print('Missing key in secret_run_params.json: "decrypt_key"', file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Invalid private key format: {e}", file=sys.stderr)
        sys.exit(1)

    logging.info(f"Decrypting input file '{args.input_filename}'")

    try:
        # Read encrypted file components
        with open(args.input_filename, 'rb') as f:
            enc_session_key = f.read(private_key.size_in_bytes())
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        # Decrypt session key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt file data
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        
        logging.info(f"Decrypted contents resulted in {len(data)} bytes")
        
        # Write decrypted data
        Path(args.output_filename).write_bytes(data)
        logging.info(f"Wrote decrypted contents to '{args.output_filename}'")

    except Exception as e:
        print(f"Decryption failed: {str(e)}", file=sys.stderr)
        sys.exit(1)