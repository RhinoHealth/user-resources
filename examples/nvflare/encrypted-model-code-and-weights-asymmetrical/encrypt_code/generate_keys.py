#!/usr/bin/env python
import argparse
import logging
import sys
from pathlib import Path
from Crypto.PublicKey import RSA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RSA key pair")
    parser.add_argument(
        "-priv", 
        "--private-key", 
        required=True,
        type=str, 
        help="Path to save private key (e.g., private.pem)"
    )
    parser.add_argument(
        "-pub", 
        "--public-key", 
        required=True,
        type=str, 
        help="Path to save public key (e.g., public.pem)"
    )
    args = parser.parse_args()

    # Generate RSA key pair
    key = RSA.generate(2048)
    
    # Save private key
    logging.info(f"Writing private key to {args.private_key}")
    with open(args.private_key, 'wb') as f:
        f.write(key.export_key('PEM'))
    
    # Save public key
    logging.info(f"Writing public key to {args.public_key}")
    with open(args.public_key, 'wb') as f:
        f.write(key.publickey().export_key('PEM'))

    logging.info("Done")
    sys.exit(0)