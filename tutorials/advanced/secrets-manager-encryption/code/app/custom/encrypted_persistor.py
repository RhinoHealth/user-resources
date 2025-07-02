import json
import os
import torch
from typing import Any
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import nvflare.app_opt.pt.file_model_persistor as mp

class EncryptedPersistor(mp.PTFileModelPersistor):
    def _load_encryption_key(self) -> RSA.RsaKey:
        """Load RSA public key from secret params file."""
        secret_path = Path("/server-credentials/secret_run_params.json")
        if not secret_path.exists():
            raise ValueError(f"Secret params file not found at {secret_path}")
        
        with open(secret_path, 'r') as f:
            params = json.load(f)
            
        if 'encrypt_key' not in params:
            raise ValueError("encrypt_key not found in secret params")
            
        return RSA.import_key(params['encrypt_key'])

    def save_model_file(self, save_path: str):
        """Override save_model_file to encrypt the model using RSA/AES hybrid encryption."""
        # First save the model state dict to temp file
        temp_location = f"{save_path}.temp"
        save_dict = self.persistence_manager.to_persistence_dict()
        torch.save(save_dict, temp_location)
        
        # Read the saved model file
        with open(temp_location, 'rb') as f:
            data = f.read()
            
        # Generate random AES session key
        session_key = get_random_bytes(16)
        
        # Encrypt session key with RSA
        public_key = self._load_encryption_key()
        cipher_rsa = PKCS1_OAEP.new(public_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        
        # Encrypt file data with AES
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        
        # Save encrypted data
        with open(save_path, 'wb') as f:
            [f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
            
        # Clean up temp file
        os.remove(temp_location)