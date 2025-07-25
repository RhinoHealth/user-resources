import os
import pandas as pd
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from nvflare.client.api import Client
from custom.network import PneumoniaModel, PneumoniaDataset


class PneumoniaTrainer(Client):
    def __init__(self):
        super().__init__()
        self.model = PneumoniaModel()

    def train(self, data_path, model_path, num_epochs=5, batch_size=8, lr=1e-4):
        df = pd.read_csv(os.path.join(data_path, "dataset.csv"))
        transform = transforms.Compose([transforms.ToTensor()])
        dataset = PneumoniaDataset(df, transform=transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = torch.nn.BCELoss()

        self.model.train()
        for epoch in range(num_epochs):
            for images, labels in dataloader:
                outputs = self.model(images)
                loss = criterion(outputs.squeeze(), labels.float())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        torch.save(self.model.state_dict(), os.path.join(model_path, "model.pth"))

    def execute(self, task_name, data, fl_ctx):
        if task_name == "train":
            data_path = fl_ctx.get_prop("DATA_PATH")
            model_path = fl_ctx.get_prop("MODEL_PATH")
            self.train(data_path, model_path)
        return {"status": "success"}
