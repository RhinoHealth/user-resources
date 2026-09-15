import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os


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
    data_dir = 'data/BreastMNIST'
    num_epochs = 10
    batch_size = 32
    learning_rate = 1e-3

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    train_dataset = BreastMNISTDataset(os.path.join(data_dir, 'train'), transform)
    val_dataset = BreastMNISTDataset(os.path.join(data_dir, 'val'), transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SimpleCNN().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.float().unsqueeze(1).to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

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

        print(f"Epoch {epoch+1}/{num_epochs} "
              f"| Train Loss: {train_loss/len(train_loader):.4f} "
              f"| Val Loss: {val_loss/len(val_loader):.4f} "
              f"| Val Acc: {correct/total:.4f}")

    torch.save(model.state_dict(), 'model.pt')
    print("Model saved to model.pt")