import torch
from torch.utils.data import DataLoader, TensorDataset, Subset
import torch.nn as nn
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import random
import numpy as np
import logging
import sys

class SimpleClassifier(nn.Module):
    def __init__(self, input_dim=20, hidden_dim=8, output_dim=3):
        torch.manual_seed(45)
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
    
class ClassificationTrainer:
    def __init__(self, model, learning_rate=0.01):
        self.model = model
        self.optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
    
    def train(self, dataloader, epochs=1):
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for x, y in dataloader:
                self.optimizer.zero_grad()
                outputs = self.model(x)
                loss = self.criterion(outputs, y)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            avg_loss = total_loss / len(dataloader)
    
    def evaluate(self, dataloader):
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in dataloader:
                outputs = self.model(x)
                _, predicted = torch.max(outputs, 1)
                total += y.size(0)
                correct += (predicted == y).sum().item()
        accuracy = correct / total
        return accuracy


def create_loader(X_train, X_test, y_train, y_test, batch_size=32):
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.LongTensor(y_test)
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
    return DataLoader(train_dataset, batch_size=batch_size, shuffle=True), DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

def get_datasets(site_name):
# Generate synthetic classification data
    X, y = make_classification(
        n_samples=6000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=3,
        n_clusters_per_class=2,
        class_sep=1.0,
        random_state=42
    )

    class_0_mask = y == 0
    class_1_mask = y == 1
    class_2_mask = y == 2

    X_class_0 = X[class_0_mask]
    y_class_0 = y[class_0_mask]
    X_class_1 = X[class_1_mask]
    y_class_1 = y[class_1_mask]
    X_class_2 = X[class_2_mask]
    y_class_2 = y[class_2_mask]
   
    if site_name == "site-1":
        X_train = np.vstack([X_class_0[:600], X_class_1[:130], X_class_2[:130]])
        y_train = np.hstack([y_class_0[:600], y_class_1[:130], y_class_2[:130]])
        X_test = np.vstack([X_class_0[600:700], X_class_1[130:350], X_class_2[130:350]])
        y_test = np.hstack([y_class_0[600:700], y_class_1[130:350], y_class_2[130:350]])

    elif site_name == "site-2":
        X_train = np.vstack([X_class_1[350:950], X_class_0[700:830], X_class_2[350:480]])
        y_train = np.hstack([y_class_1[350:950], y_class_0[700:830], y_class_2[350:480]])
        X_test = np.vstack([X_class_1[950:1050], X_class_0[830:1050], X_class_2[480:700]])
        y_test = np.hstack([y_class_1[950:1050], y_class_0[830:1050], y_class_2[480:700]])

    elif site_name == "site-3":
        X_train = np.vstack([X_class_2[700:1300], X_class_0[1050:1180], X_class_1[1050:1180]])
        y_train = np.hstack([y_class_2[700:1300], y_class_0[1050:1180], y_class_1[1050:1180]])
        X_test = np.vstack([X_class_2[1300:1400], X_class_0[1180:1400], X_class_1[1180:1400]])
        y_test = np.hstack([y_class_2[1300:1400], y_class_0[1180:1400], y_class_1[1180:1400]])


    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.LongTensor(y_test)
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=True)



    return train_loader, test_loader


class LoggerFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('Finished')
    
def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    task_logger = logging.getLogger("__main__.ClientTaskWorker")
    task_logger.addFilter(LoggerFilter())
    
    return logger