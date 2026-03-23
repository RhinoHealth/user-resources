# Copyright (c) 2025, Rhino HealthTech, Inc.
# Original file modified by Rhino to adapt it to the Rhino Federated Computing Platform.
# 
# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
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
from collections import OrderedDict
from logging import INFO
import os

import torch
import torch.nn as nn
from flwr.common.logger import log
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import CenterCrop, Compose, Normalize, RandomRotation, Resize, ToTensor

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class Net(nn.Module):
    def __init__(self, num_classes=2):
        super(Net, self).__init__()

        # Conv Layer 1
        self.conv1 = nn.Conv2d(3, 12, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(12)
        self.relu1 = nn.ReLU()

        # Conv Layer 2
        self.conv2 = nn.Conv2d(12, 20, 3, padding=1)
        self.relu2 = nn.ReLU()

        # Conv Layer 3
        self.conv3 = nn.Conv2d(20, 32, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(32)
        self.relu3 = nn.ReLU()

        # Fully Connected Layer
        self.fc = nn.Linear(32 * 112 * 112, num_classes)

        # Max Pooling
        self.pool = nn.MaxPool2d(2, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pass through Conv1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool(x)

        # Pass through Conv2
        x = self.conv2(x)
        x = self.relu2(x)

        # Pass through Conv3
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu3(x)

        # Flatten before passing to fully connected layer
        x = x.view(-1, 32 * 112 * 112)

        # Pass through Fully Connected Layer
        x = self.fc(x)

        return x


def load_data():

    # Create data loaders for the training and testing sets.
    trf = Compose(
        [
            Resize(size=(256, 256)),
            RandomRotation(degrees=(-20, +20)),
            CenterCrop(size=224),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    # Get the list of dataset UIDs, assuming each client has separate train and test datasets
    dataset_uids = next(os.walk('/input/datasets'))[1]

    # Ensure there are at least two datasets
    if len(dataset_uids) < 2:
        raise ValueError("Not enough datasets found in '/input/datasets'.")

    # Assign train and test UIDs
    train_uid = dataset_uids[0]
    test_uid = dataset_uids[1]

    # Define paths
    train_path = f'/input/datasets/{train_uid}/file_data/'
    test_path = f'/input/datasets/{test_uid}/file_data/'

    print("Train Path:", train_path)
    print("Test Path:", test_path)

    # Load datasets using ImageFolder
    trainset = ImageFolder(root=train_path, transform=trf)
    testset = ImageFolder(root=test_path, transform=trf)

    # Create DataLoaders
    train_loader = DataLoader(trainset, batch_size=32, shuffle=True)
    test_loader = DataLoader(testset, batch_size=32, shuffle=False)

    return train_loader, test_loader


def train(net, trainloader, valloader, epochs, device):
    """Train the model on the training set."""
    log(INFO, "Starting training...")
    net.to(device)  # move model to GPU if available
    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    net.train()
    for _ in range(epochs):
        for images, labels in trainloader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()

    train_loss, train_acc = test(net, trainloader)
    val_loss, val_acc = test(net, valloader)

    results = {
        "train_loss": train_loss,
        "train_accuracy": train_acc,
        "val_loss": val_loss,
        "val_accuracy": val_acc,
    }
    return results


def test(net, testloader):
    """Validate the model on the test set."""
    net.to(DEVICE)
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0
    with torch.no_grad():
        for images, labels in testloader:
            outputs = net(images.to(DEVICE))
            labels = labels.to(DEVICE)
            loss += criterion(outputs, labels).item()
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
    accuracy = correct / len(testloader.dataset)
    return loss, accuracy


def get_weights(net):
    return [val.cpu().numpy() for _, val in net.state_dict().items()]


def set_weights(net, parameters):
    params_dict = zip(net.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    net.load_state_dict(state_dict, strict=True)


