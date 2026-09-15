#!/usr/bin/env python
import sys
from pathlib import Path
from cryptography.fernet import Fernet
import json
import pandas as pd
import torch
import torchvision
from torch.utils.data.dataloader import DataLoader
from torchvision.transforms import ToTensor, Normalize, Compose, Resize, CenterCrop

from network import PneumoniaModel


def _rel_key(path):
    """Return the '<class>/<filename>' tail of a path, used to match scores
    back to dataset.csv rows regardless of any leading split prefix."""
    parts = path.replace("\\", "/").split("/")
    return "/".join(parts[-2:])


def decrypt_weights(model_parameters_path):
    secret_run_params_file_path = Path("/input/secret_run_params.json")
    if secret_run_params_file_path.is_file():
        with secret_run_params_file_path.open("rb") as secret_run_params_file:
            secret_run_params = json.load(secret_run_params_file)
            key = secret_run_params["key"]
            fernet = Fernet(key)
            encrypted = Path(model_parameters_path).read_bytes()
            decrypted = fernet.decrypt(encrypted)
            model_parameters_path = '/output/model_parameters.pt'
            Path(model_parameters_path).write_bytes(decrypted)
    return model_parameters_path


def infer(model_params_file_path):
    # Setup the model
    model = PneumoniaModel()
    model.load_state_dict(torch.load(decrypt_weights(model_params_file_path))["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # Preparing the dataset for testing.
    # Note: RandomRotation is a training-time augmentation and has been
    # removed here - applying it at inference time would make scores
    # non-deterministic (a different random rotation, and therefore a
    # different score, every time the same image is scored).
    transforms = Compose([
        Resize(size=(256, 256)),
        CenterCrop(size=224),
        ToTensor(),
        Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    tabular_data = pd.read_csv("/input/dataset.csv")
    dataset = torchvision.datasets.ImageFolder(root="/input/file_data", transform=transforms)
    loader = DataLoader(dataset, batch_size=4, shuffle=False)

    # ImageFolder enumerates images grouped by class, which does NOT match
    # dataset.csv's row order. Score every image and key each score by its
    # '<class>/<filename>' path so it can be matched back to the correct row,
    # rather than assuming loader order == dataset.csv row order.
    sample_paths = [_rel_key(path) for path, _ in dataset.samples]
    scores_by_path = {}
    idx = 0
    with torch.no_grad():
        for images, _ in loader:
            images = images.to(device)
            output = model(images)
            batch_scores = torch.select(output, 1, 1)
            for score in batch_scores:
                scores_by_path[sample_paths[idx]] = score.item()
                idx += 1

    tabular_data["Model_Score"] = tabular_data["image_name"].apply(
        lambda name: scores_by_path.get(_rel_key(name))
    )

    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_weights_file_path,) = args
    infer(model_weights_file_path)
    sys.exit(0)
