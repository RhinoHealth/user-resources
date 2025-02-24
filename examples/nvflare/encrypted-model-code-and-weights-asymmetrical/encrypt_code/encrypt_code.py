from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import argparse

def encrypt_file(input_file, public_key_file, output_file):
    # Read the input file
    with open(input_file, 'rb') as f:
        data = f.read()

    # Import the public key
    with open(public_key_file) as f:
        public_key = RSA.import_key(f.read())
    
    # Create session key
    session_key = get_random_bytes(16)
    
    # Encrypt the session key with RSA
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the file data with AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    
    # Save the encrypted data
    with open(output_file, "wb") as f:
        [f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]

def decrypt_file(input_file, private_key_file, output_file):
    # Import private key
    with open(private_key_file) as f:
        private_key = RSA.import_key(f.read())

    # Read the encrypted data
    with open(input_file, "rb") as f:
        enc_session_key, nonce, tag, ciphertext = [
            f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)
        ]
    
    # Decrypt session key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    
    # Decrypt data
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    
    # Save decrypted file
    with open(output_file, 'wb') as f:
        f.write(data)

def main():
    parser = argparse.ArgumentParser(description='Encrypt/Decrypt files using hybrid RSA/AES encryption')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-k', '--key', required=True, help='Public/Private key file path')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt mode (default is encrypt)')
    
    args = parser.parse_args()
    
    if args.decrypt:
        decrypt_file(args.input, args.key, args.output)
    else:
        encrypt_file(args.input, args.key, args.output)

if __name__ == '__main__':
    main()