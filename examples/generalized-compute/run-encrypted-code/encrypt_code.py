#!/usr/bin/env python
import argparse
from cryptography.fernet import Fernet
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Encrypt a file given a key')

    parser.add_argument('input_filename', help="input filename")
    parser.add_argument('key_file', help="encryption key filename")
    parser.add_argument('output_filename', help="output filename")

    args = parser.parse_args()

    with open(args.key_file, 'rb') as keyfile:
        key = keyfile.read()

    fernet = Fernet(key)

    logging.info(f"Processing input file '{args.input_filename}'")
    with open(args.input_filename, 'rb') as input_file:
        original = input_file.read()
        logging.info(f"Read {len(original)} bytes")

    encrypted = fernet.encrypt(original)
    logging.info(f"Encrypted content resulted in {len(encrypted)} bytes")

    logging.info(f"Writing encrypted contents to output file '{args.output_filename}'")
    with open(args.output_filename, 'wb') as output_file:
        output_file.write(encrypted)

    logging.info("Done")
    sys.exit(0)
