#!/usr/bin/env python
import sys

import pandas as pd
import torch
import torchvision
import json

from network import PneumoniaModel
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from torch.utils.data.dataloader import DataLoader
from torchvision.transforms import (
    CenterCrop,
    Compose,
    Normalize,
    RandomRotation,
    Resize,
    ToTensor,
)


def decrypt_weights(model_parameters_path):
    secret_run_params_file_path = Path("/input/secret_run_params.json")
    if secret_run_params_file_path.is_file():
        # Load private key from JSON
        with secret_run_params_file_path.open("rb") as secret_run_params_file:
            secret_run_params = json.load(secret_run_params_file)
            private_key = RSA.import_key(secret_run_params["decrypt_key"])

        # Read encrypted file
        with open(model_parameters_path, 'rb') as f:
            enc_session_key = f.read(private_key.size_in_bytes())
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        # Decrypt session key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt data
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

        # Save decrypted data
        output_path = '/output/model_parameters.pt'
        Path(output_path).write_bytes(decrypted)
        return output_path
    return model_parameters_path


def infer(model_params_file_path):
    # Setup the model
    model = PneumoniaModel()
    model.load_state_dict(torch.load(decrypt_weights(model_params_file_path))["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # Preparing the dataset for testing.
    transforms = Compose(
        [
            Resize(size=(256, 256)),
            RandomRotation(degrees=(-20, +20)),
            CenterCrop(size=224),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    tabular_data = pd.read_csv("/input/dataset.csv")
    dataset = torchvision.datasets.ImageFolder(
        root="/input/file_data", transform=transforms
    )
    loader = DataLoader(dataset, batch_size=4, shuffle=False)

    # Inference: Apply model and add scores column.
    scores = []
    with torch.no_grad():
        for i, (images, labels) in enumerate(loader):
            images = images.to(device)
            predictions = model(images)
            batch_scores = torch.select(predictions, 1, 1)
            scores.extend([score.item() for score in batch_scores])
    tabular_data["Model Score"] = scores

    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
