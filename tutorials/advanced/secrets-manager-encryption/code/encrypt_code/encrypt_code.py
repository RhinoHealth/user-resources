from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import argparse
import boto3
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

class SecretsManager:
    def __init__(self, role_arn, region='us-east-1'):
        try:
            self.role_arn = role_arn
            self.client = self._get_client(region)
        except Exception as e:
            logging.error(f"Failed to initialize secrets manager: {str(e)}")
            raise

    def _get_client(self, region):
        try:
            sts_client = boto3.client('sts')
            credentials = sts_client.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName='KeyGenerationSession'
            )['Credentials']
            
            session = boto3.session.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=region
            )
            return session.client('secretsmanager')
        except Exception as e:
            logging.error(f"Failed to get client: {str(e)}")
            raise

    def get_or_create_key(self, key_name):
        """Get existing or create new public key"""
        try:
            # Try to get existing secret
            try:
                secret = self.client.get_secret_value(SecretId=key_name)
                
                # Validate secret response structure
                if 'SecretString' not in secret:
                    raise ValueError(f"Secret '{key_name}' does not contain SecretString")
                
                try:
                    secret_dict = json.loads(secret['SecretString'])
                except json.JSONDecodeError as e:
                    raise ValueError(f"Secret '{key_name}' contains invalid JSON: {str(e)}")
                
                # Validate required keys exist
                if 'encrypt_key' not in secret_dict:
                    raise ValueError(f"Secret '{key_name}' does not contain 'encrypt_key'")
                
                try:
                    return RSA.import_key(secret_dict['encrypt_key'])
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Secret '{key_name}' contains invalid RSA public key: {str(e)}")
                    
            except self.client.exceptions.ResourceNotFoundException:
                # Secret doesn't exist, create new key pair
                return self._create_new_key_pair(key_name)
                
        except Exception as e:
            logging.error(f"Failed to get/create public key: {str(e)}")
            raise

    def _create_new_key_pair(self, key_name):
        """Generate and store new key pair with PEM formatting intact"""
        logging.info(f"Key '{key_name}' not found, generating new key pair")
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()
        
        # Store keys directly in the secret with the specified structure
        secret_dict = {
            'encrypt_key': public_key.export_key().decode('utf-8'),
            'decrypt_key': private_key.export_key().decode('utf-8')
        }
        
        try:
            # Create new secret in AWS Secrets Manager
            self.client.create_secret(
                Name=key_name,
                SecretString=json.dumps(secret_dict),
                Description=f'RSA key pair for {key_name}'
            )
        except Exception as e:
            logging.error(f"Failed to create new key pair: {str(e)}")
            raise
        
        logging.info(f"Generated and stored new key pair for '{key_name}'")
        return public_key

def encrypt_file(input_file, key_name, output_file, delete_input=False):
    """Encrypt a file using hybrid RSA/AES encryption
    
    Args:
        input_file (str): Path to input file
        key_name (str): Name of key in AWS Secrets Manager (used as secret ID)
        output_file (str): Path to output encrypted file
        delete_input (bool): Whether to delete input file after encryption
    """
    # NOTE:Manually set the Secret Manager details
    ACCOUNT_ID = '<account_id>'
    ROLE_NAME = '<role_name>'

    try:
        # Initialize secrets manager
        secrets = SecretsManager(
            role_arn=f'arn:aws:iam::{ACCOUNT_ID}:role/{ROLE_NAME}'
        )
    except Exception as e:
        logging.error(f"Failed to initialize secrets manager: {str(e)}")
        raise

    try:
        # Read input file
        with open(input_file, 'rb') as f:
            data = f.read()
    except Exception as e:
        logging.error(f"Failed to read input file: {str(e)}")
        raise

    # Get public key and generate session key
    public_key = secrets.get_or_create_key(key_name)
    session_key = get_random_bytes(16)
    
    # Encrypt session key with RSA
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt file data with AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    
    # Save encrypted data
    with open(output_file, "wb") as f:
        [f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    
    # Delete input file if requested
    if delete_input:
        Path(input_file).unlink()
        logging.info(f"Deleted input file: {input_file}")

def main():
    parser = argparse.ArgumentParser(description='Encrypt files using hybrid RSA/AES encryption')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-k', '--key-name', required=True, help='Key name in AWS Secrets Manager (used as secret ID)')
    parser.add_argument('-d', '--delete', action='store_true', help='Delete input file after encryption')
    
    args = parser.parse_args()
    encrypt_file(args.input, args.key_name, args.output, args.delete)

if __name__ == '__main__':
    main()