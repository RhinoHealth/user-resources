import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from PIL import Image
import os

class PneumoniaModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 74 * 74, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 74 * 74)
        x = F.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(x))


class PneumoniaDataset(Dataset):
    def __init__(self, dataframe, transform=None):
        self.dataframe = dataframe
        self.transform = transform

    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        img = Image.open(row["JPG file"]).convert("L")
        label = 1 if row["Pneumonia"] == "true" or row["Pneumonia"] is True else 0
        if self.transform:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.dataframe)
