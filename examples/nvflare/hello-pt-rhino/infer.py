#!/usr/bin/env python
import shutil
import sys
from pathlib import Path

import pandas as pd
import torch
import torchvision
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, ToTensor, Normalize

from simple_network import SimpleNetwork


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

    # Inference: Apply model and add scores column.
    scores = []
    with torch.no_grad():
        for i, (images, labels) in enumerate(loader):
            images = images.to(device)
            output = model(images)
            batch_scores = torch.select(output, 1, 1)
            scores.extend([score.item() for score in batch_scores])
    tabular_data['Model_Score'] = scores

    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
