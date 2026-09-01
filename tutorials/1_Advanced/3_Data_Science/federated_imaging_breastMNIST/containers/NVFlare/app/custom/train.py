import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os
from pathlib import Path

# Step 1: Import the NVFlare Client API
import nvflare.client as flare


class BreastMNISTDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.samples = [
            (f, int(f.split('_label_')[-1].replace('.png', '')))
            for f in os.listdir(image_dir) if f.endswith('.png')
        ]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        filename, label = self.samples[idx]
        img = Image.open(os.path.join(self.image_dir, filename)).convert('L')
        if self.transform:
            img = self.transform(img)
        return img, label


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128), nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.net(x)


if __name__ == '__main__':
    data_dir = [x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()][0]
    num_epochs = 3
    batch_size = 32
    learning_rate = 1e-3

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    train_dataset = BreastMNISTDataset(os.path.join(data_dir, 'file_data/train'), transform)
    val_dataset = BreastMNISTDataset(os.path.join(data_dir, 'file_data/val'), transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SimpleCNN().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Step 2: Initialize the NVFlare client API
    flare.init()

    # Step 3: Replace epoch loop with flare.is_running()
    while flare.is_running():

        # Step 4: Receive the global model weights from the NVFlare server
        input_model = flare.receive()

        # Step 5: Load the global weights into the local model
        global_weights = input_model.params
        model.load_state_dict(global_weights)

        # Step 6: Run validation before training to evaluate the global model
        model.eval()
        val_loss, correct, total = 0, 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.float().unsqueeze(1).to(device)
                outputs = model(images)
                val_loss += criterion(outputs, labels).item()
                preds = (torch.sigmoid(outputs) > 0.5).long()
                correct += (preds == labels.long()).sum().item()
                total += labels.size(0)

        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = correct / total
        val_samples = total

        model.train()
        train_loss, total_samples = 0, 0
        for epoch in range(num_epochs):
            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.float().unsqueeze(1).to(device)
                optimizer.zero_grad()
                loss = criterion(model(images), labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
                total_samples += labels.size(0)

        avg_train_loss = train_loss / len(train_loader)

        print(f"Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_accuracy:.4f}")

        # Step 7: Create the output FLModel with locally trained weights and metrics
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

        # Step 8: Send the output model to the NVFlare server for aggregation
        flare.send(output_model)