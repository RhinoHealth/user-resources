#!/usr/bin/env python
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
    
    # Load model - handle both old and new client API formats
    try:
        model_data = torch.load(model_params_file_path)
        if isinstance(model_data, dict):
            if "model" in model_data:
                # Old format from traditional executor
                model.load_state_dict(model_data["model"])
            else:
                # New format from client API (direct state_dict)
                model.load_state_dict(model_data)
        else:
            # Fallback: assume it's a direct state_dict
            model.load_state_dict(model_data)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise
    
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
        print(f"✅ Loaded tabular data: {len(tabular_data)} rows")
    except Exception as e:
        print(f"❌ Error loading dataset.csv: {e}")
        raise
    
    try:
        dataset = torchvision.datasets.ImageFolder(
            root="/input/file_data", transform=transforms
        )
        print(f"✅ Loaded image dataset: {len(dataset)} images")
    except Exception as e:
        print(f"❌ Error loading image dataset: {e}")
        raise
    
    loader = DataLoader(dataset, batch_size=4, shuffle=False)

    # Inference: Apply model and add scores column.
    scores = []
    with torch.no_grad():
        for i, (images, labels) in enumerate(loader):
            images = images.to(device)
            predictions = model(images)
            batch_scores = torch.select(predictions, 1, 1)
            scores.extend([score.item() for score in batch_scores])
    
    print(f"✅ Generated {len(scores)} predictions")
    
    # Add scores to tabular data
    if len(scores) == len(tabular_data):
        tabular_data["Model Score"] = scores
    else:
        print(f"⚠️ Warning: Mismatch between scores ({len(scores)}) and tabular data ({len(tabular_data)})")
        # Pad or truncate as needed
        tabular_data["Model Score"] = (scores + [0.0] * len(tabular_data))[:len(tabular_data)]

    tabular_data.to_csv("/output/dataset.csv", index=False)
    print("✅ Results saved to /output/dataset.csv")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        # Auto-discover model file in input directory
        model_patterns = [
            "/input/model_parameters*.pt",
            "/input/checkpoint*.pt"
        ]
        
        model_path = None
        for pattern in model_patterns:
            model_files = glob.glob(pattern)
            if model_files:
                model_path = sorted(model_files)[-1]  # Get the most recent
                break
        
        if model_path is None:
            print("❌ ERROR: No model file found in /input/")
            sys.exit(1)
    
    print(f"🎯 Using model: {model_path}")
    infer(model_path)
    print("🎉 Inference completed successfully!")
    sys.exit(0)
