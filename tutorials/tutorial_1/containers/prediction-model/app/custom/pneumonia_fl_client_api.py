# Copyright (c) 2025, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import pandas as pd
import torch
import torchvision
from pathlib import Path
from network import PneumoniaModel
from sklearn.model_selection import train_test_split
from torch import nn
from torch.optim import Adam
from torch.utils.data.dataloader import DataLoader
from torchvision.transforms import (
    CenterCrop,
    Compose,
    Normalize,
    RandomRotation,
    Resize,
    ToTensor,
)

# (1) import nvflare client API
import nvflare.client as flare

from nvflare.app_common.abstract.model import make_model_learnable
from nvflare.app_opt.pt.model_persistence_format_manager import PTModelPersistenceFormatManager


def load_data(test_set_percentage=20.0):
    """Load pneumonia data from input directory"""
    # Try tutorial format first: /input/datasets/ with CSV files
    dataset_dirs = [x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()]
    for dataset_dir in dataset_dirs:
        dataset_df = pd.read_csv(dataset_dir / "dataset.csv")

        dataset_df["JPG file_abspath"] = dataset_dir / "file_data" / dataset_df["JPG file"]
        train_df, test_df = train_test_split(dataset_df, test_size=test_set_percentage / 100)

        train_image_file_paths = train_df["JPG file_abspath"]
        test_image_file_paths = test_df["JPG file_abspath"]

        # Create datasets by creating directories with symlinks
        train_dataset_folder = Path("/tmp/train_images_symlinks")
        test_dataset_folder = Path("/tmp/test_images_symlinks")
        
        for image_file_path in train_image_file_paths:
            symlink_path = train_dataset_folder / image_file_path.relative_to(Path(dataset_dir / "file_data"))
            symlink_path.parent.mkdir(parents=True, exist_ok=True)
            if not symlink_path.exists():
                symlink_path.symlink_to(image_file_path)
                
        for image_file_path in test_image_file_paths:
            symlink_path = test_dataset_folder / image_file_path.relative_to(Path(dataset_dir / "file_data"))
            symlink_path.parent.mkdir(parents=True, exist_ok=True)
            if not symlink_path.exists():
                symlink_path.symlink_to(image_file_path)

    transforms = Compose([
        Resize(size=(256, 256)),
        RandomRotation(degrees=(-20, +20)),
        CenterCrop(size=224),
        ToTensor(),
        Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    train_dataset = torchvision.datasets.ImageFolder(Path(train_dataset_folder), transform=transforms)
    test_dataset = torchvision.datasets.ImageFolder(Path(test_dataset_folder), transform=transforms)
    
    print(f"Loaded datasets with tutorial format: {len(train_dataset)} train, {len(test_dataset)} test")
    return train_dataset, test_dataset



if __name__ == "__main__":
    # (2) Initialize NVFlare client API
    flare.init()
    
    # Initialize model and device
    model = PneumoniaModel()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # Load data
    train_dataset, test_dataset = load_data()
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)
    
    print(f"Initialized with {len(train_dataset)} training samples, {len(test_dataset)} test samples")
    
    # Setup training components
    loss_fn = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=0.001)  # Reduced learning rate
    
    # Add learning rate scheduler for better convergence
    from torch.optim.lr_scheduler import StepLR
    scheduler = StepLR(optimizer, step_size=5, gamma=0.5)  # Reduce LR every 5 rounds    
    # (3) Federated learning loop
    while flare.is_running():
        # (4) Receive FLModel from NVFlare
        input_model = flare.receive()
        current_round = input_model.current_round
        
        print(f"Round {current_round} started")
        
        # (5) Load global model weights
        global_weights = input_model.params
        if global_weights:
            # Convert numpy arrays back to torch tensors before loading
            torch_weights = {k: torch.as_tensor(v) for k, v in global_weights.items()}
            model.load_state_dict(torch_weights)
            print("Loaded global model weights")
        
        # (6) Local training
        model.train()
        total_loss = 0.0
        total_samples = 0
        num_batches = 0
        
        for i, (batch_images, batch_labels) in enumerate(train_loader):
            batch_images = batch_images.to(device)
            batch_labels = batch_labels.to(device)
            
            optimizer.zero_grad()
            predictions = model(batch_images)
            loss = loss_fn(predictions, batch_labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * batch_images.size(0)  # Multiply by batch size for proper averaging
            total_samples += batch_images.size(0)
            num_batches += 1
            
            if (i + 1) % 10 == 0:
                avg_loss_so_far = total_loss / total_samples
                print(f"Batch {i+1}, Loss: {avg_loss_so_far:.4f}")
        
        avg_train_loss = total_loss / total_samples if total_samples > 0 else 0.0
        
        # (7) Local validation
        model.eval()
        val_loss = 0.0
        val_samples = 0
        correct_predictions = 0
        
        with torch.no_grad():
            for batch_images, batch_labels in test_loader:
                batch_images = batch_images.to(device)
                batch_labels = batch_labels.to(device)
                predictions = model(batch_images)
                loss = loss_fn(predictions, batch_labels)
                val_loss += loss.item() * batch_images.size(0)  
                val_samples += batch_images.size(0)
                
                # Calculate accuracy
                _, predicted_classes = torch.max(predictions, 1)
                correct_predictions += (predicted_classes == batch_labels).sum().item()
        
        avg_val_loss = val_loss / val_samples if val_samples > 0 else 0.0
        val_accuracy = correct_predictions / val_samples if val_samples > 0 else 0.0
        
        print(f"Round {current_round} - Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")
        
        
        # (8) Create output FLModel with trained weights and metrics
        output_model = flare.FLModel(
            params=model.state_dict(),
            metrics={
                "train_loss": avg_train_loss, 
                "val_loss": avg_val_loss,
                "val_accuracy": val_accuracy,
                "train_samples": total_samples,
                "val_samples": val_samples
            }
        )
        
        # (9) Send model back to NVFlare
        flare.send(output_model)
        
        # Update learning rate scheduler
        scheduler.step()
        
        print(f"Round {current_round} completed")
    
    print("Federated learning completed!")