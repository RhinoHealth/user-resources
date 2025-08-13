# Copyright (c) 2025, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

import sys
import glob
import pandas as pd
import torch
import torchvision
from network import PneumoniaModel
from torch.utils.data.dataloader import DataLoader
from torchvision.transforms import (
    CenterCrop,
    Compose,
    Normalize,
    RandomRotation,
    Resize,
    ToTensor,
)

def infer(model_params_file_path):
    # Setup the model
    model = PneumoniaModel()
    model.load_state_dict(torch.load(model_params_file_path)["model"])
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
    
    # Load input data
    try:
        tabular_data = pd.read_csv("/input/dataset.csv")
    except Exception as e:
        print(f" Error loading dataset.csv: {e}")
        raise
    print(f" Loaded tabular data: {len(tabular_data)} rows")

    try:
        dataset = torchvision.datasets.ImageFolder(
            root="/input/file_data", transform=transforms
        )
        print(f" Loaded image dataset: {len(dataset)} images")
    except Exception as e:
        print(f" Error loading image dataset: {e}")
        raise
    
    tabular_data = tabular_data.sort_values(by="JPG file")
    loader = DataLoader(dataset, batch_size=4, shuffle=False)

    # Inference: Apply model and add scores column.
    scores = []
    with torch.no_grad():
        for i, (images, labels) in enumerate(loader):
            images = images.to(device)
            predictions = model(images)
            batch_scores = torch.select(torch.softmax(predictions, 1), 1, 1)
            scores.extend([score.item() for score in batch_scores])
    print(f" Generated {len(scores)} predictions")
    
    tabular_data["Model Score"] = scores
    tabular_data.to_csv("/output/dataset.csv", index=False)
    print(" Results saved to /output/dataset.csv")

if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
