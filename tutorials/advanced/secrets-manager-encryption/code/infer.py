#!/usr/bin/env python
import json
import sys
from pathlib import Path

from lightning import pytorch as pl
import numpy as np
import pandas as pd
import torch
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

from chemprop import data, featurizers
from chemprop_fl_classification import ClassificationMPNN, load_data_from_path

def decrypt_weights(model_parameters_path):
    secret_run_params_file_path = Path("/input/secret_run_params.json")
    if secret_run_params_file_path.is_file():
        # Load private key from JSON
        with secret_run_params_file_path.open("r") as secret_run_params_file:
            secret_run_params = json.load(secret_run_params_file)
            private_key = RSA.import_key(secret_run_params["decrypt_key"])

        # Read the encrypted file
        with open(model_parameters_path, 'rb') as f:
            # Read the RSA-encrypted session key
            enc_session_key = f.read(private_key.size_in_bytes())
            # Read the rest of the encryption data
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        # Decrypt the session key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)

        # Return decrypted data as BytesIO stream
        from io import BytesIO
        return BytesIO(data)
    return model_parameters_path

def infer(model_params_file_path):
    # Setup the model
    model = ClassificationMPNN()
    decrypted_data = decrypt_weights(model_params_file_path)
    model.load_state_dict(torch.load(decrypted_data)["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # Preparing the dataset for testing.
    tabular_data = pd.read_csv("/input/dataset.csv")
    test_data = load_data_from_path("/input/dataset.csv", "smiles", ["cyp3a4"])

    # inference code
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    test_dset = data.MoleculeDataset(test_data, featurizer)
    test_loader = data.build_dataloader(
        test_dset, num_workers=0, shuffle=False, seed=42
    )
    with torch.inference_mode():
        trainer = pl.Trainer(
            logger=None, enable_progress_bar=True, accelerator="cpu", devices=1
        )
        test_preds = trainer.predict(model, test_loader)

    tabular_data["score"] = np.concatenate(test_preds, axis=0)
    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
