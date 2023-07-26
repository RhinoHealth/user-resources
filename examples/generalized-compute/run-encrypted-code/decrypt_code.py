#!/usr/bin/env python
import argparse
from cryptography.fernet import Fernet
import logging
import json
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decrypt a file using a key from the GC run parameters')

    parser.add_argument('input_filename', help="input filename")
    parser.add_argument('output_filename', help="output filename")
    key_identifier = "key"

    args = parser.parse_args()

    run_params = {}
    run_params_filename = "/input/run_params.json"
    try:
        with open(run_params_filename, "r") as run_params_file:
            run_params = json.load(run_params_file)
    except IOError:
        logging.error("No params file found")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Invalid JSON found in params file")
        sys.exit(1)

    if key_identifier not in run_params:
        logging.error(f"Identifier '{key_identifier}' not found in run parameters")
        sys.exit(1)

    key = run_params[key_identifier]

    fernet = Fernet(key)

    logging.info(f"Decrypting input file '{args.input_filename}'")
    with open(args.input_filename, 'rb') as input_file:
        encrypted = input_file.read()
        logging.info(f"Read {len(encrypted)} bytes of encrypted content")

    decrypted = fernet.decrypt(encrypted)
    logging.info(f"Decrypted contents resulted in {len(decrypted)} bytes")

    logging.info(f"Writing decrypted contents to output file '{args.output_filename}'")
    with open(args.output_filename, 'wb') as output_file:
        output_file.write(decrypted)

    logging.info("Done")
    sys.exit(0)
