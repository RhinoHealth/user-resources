#!/usr/bin/env python
import argparse
from cryptography.fernet import Fernet
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a fernet encryption key')
    parser.add_argument('key_filename', type=str, help="the output encryption key filename")

    args = parser.parse_args()

    key = Fernet.generate_key()
    logging.info(f"Generated key with {len(key)} bytes")

    logging.info(f"Writing key to {args.key_filename}")
    with open(args.key_filename, 'wb') as filekey:
        filekey.write(key)

    logging.info("Done")
    sys.exit(0)
