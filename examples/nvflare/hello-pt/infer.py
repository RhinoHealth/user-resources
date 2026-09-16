#!/usr/bin/env python
import os
import sys

import pandas as pd
import torch
import torchvision
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, ToTensor, Normalize

from simple_network import SimpleNetwork


def _rel_key(path):
    """Return the '<class>/<filename>' tail of a path, used to match scores
    back to dataset.csv rows regardless of any leading split prefix
    (e.g. 'test/3/image0.png' in the CSV vs '3/image0.png' on disk)."""
    parts = path.replace("\\", "/").split("/")
    return "/".join(parts[-2:])


def infer(model_parameters_file_path):
    # Setup the model
    model = SimpleNetwork()
    model.load_state_dict(torch.load(model_parameters_file_path)["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # Preparing the dataset for testing.
    transforms = Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
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
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
