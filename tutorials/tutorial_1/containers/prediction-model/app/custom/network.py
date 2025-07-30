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

import torch
import torch.nn as nn
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd
import os


class PneumoniaModel(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels=3, out_channels=12, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(num_features=12)
        self.relu1 = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2)
        self.conv2 = nn.Conv2d(in_channels=12, out_channels=20, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.conv3 = nn.Conv2d(in_channels=20, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(num_features=32)
        self.relu3 = nn.ReLU()
        self.fc = nn.Linear(in_features=32 * 112 * 112, out_features=num_classes)

    def forward(self, input):
        output = self.conv1(input)
        output = self.bn1(output)
        output = self.relu1(output)
        output = self.pool(output)
        output = self.conv2(output)
        output = self.relu2(output)
        output = self.conv3(output)
        output = self.bn3(output)
        output = self.relu3(output)
        output = output.view(-1, 32 * 112 * 112)
        output = self.fc(output)
        return output


class PneumoniaDataset(Dataset):
    def __init__(self, data_csv, transform=None):
        """
        Custom dataset for pneumonia detection
        
        Args:
            data_csv (str): Path to CSV file with image paths and labels
            transform: Optional transform to be applied on images
        """
        self.data_df = pd.read_csv(data_csv)
        self.transform = transform
        
        # Handle different CSV formats
        if 'image_path' in self.data_df.columns:
            self.image_paths = self.data_df['image_path'].tolist()
        elif 'JPG file' in self.data_df.columns:
            # For FCP format
            self.image_paths = self.data_df['JPG file'].tolist()
            # Convert relative paths to absolute paths if needed
            if not os.path.isabs(self.image_paths[0]):
                base_dir = os.path.dirname(data_csv)
                self.image_paths = [os.path.join(base_dir, 'file_data', path) for path in self.image_paths]
        else:
            raise ValueError("CSV must contain either 'image_path' or 'JPG file' column")
            
        # Handle different label formats
        if 'label' in self.data_df.columns:
            self.labels = self.data_df['label'].tolist()
        elif 'Pneumonia' in self.data_df.columns:
            self.labels = self.data_df['Pneumonia'].tolist()
        else:
            # If no labels, assume all are normal (0)
            self.labels = [0] * len(self.image_paths)
            
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            if self.transform:
                image = self.transform(image)
                
            return image, torch.tensor(label, dtype=torch.long)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a dummy image and label if there's an error
            dummy_image = Image.new('RGB', (224, 224), color=(0, 0, 0))
            if self.transform:
                dummy_image = self.transform(dummy_image)
            return dummy_image, torch.tensor(0, dtype=torch.long)

