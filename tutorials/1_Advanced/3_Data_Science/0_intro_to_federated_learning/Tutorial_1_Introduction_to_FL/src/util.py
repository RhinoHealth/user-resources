import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def make_plot(results: list=[]):
    if len(results) == 4:
        data = np.array([[results[0], results[3]], [results[2], results[1]]])
        xticklabels = ["Client 1", "Client 2"]
        yticklabels = ["Client 1", "Client 2"]
    else:
        data = np.array([[results[0], results[3], results[4]], 
                   [results[2], results[1], results[5]], 
                   [results[6], results[7], results[8]]])
        xticklabels = ["Client 1", "Client 2", "Global Model"]
        yticklabels = ["Client 1", "Client 2", "Centralized"]
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(data, annot=True, fmt='.3f', cmap='Blues', 
                    cbar_kws={'label': 'Accuracy'}, square=True,
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    linewidths=0.5, linecolor='gray',
                    vmin=0, vmax=1)

    plt.xlabel("Model Trained From", fontsize=12, fontweight='bold')
    plt.ylabel("Evaluated On Test Data From", fontsize=12, fontweight='bold')
    plt.title('Federated Learning: Model Performance Comparison', 
            fontsize=14, fontweight='bold', pad=20)

    plt.xticks(rotation=0, fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    plt.tight_layout()
    plt.show()




def get_datasets():
    # Create client 1 data
    X_1, y_1 = make_classification(
        n_samples=1000,      
        n_features=10,       
        n_informative=2,
        n_redundant=8,
        n_classes=2,
        random_state=315
    )
    X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(
        X_1, y_1, test_size=0.2, random_state=315
    )
    train_dataset_1 = TensorDataset(torch.FloatTensor(X_train_1), torch.LongTensor(y_train_1))
    test_dataset_1 = TensorDataset(torch.FloatTensor(X_test_1), torch.LongTensor(y_test_1))

    # Create client 2 data
    X_2, y_2 = make_classification(
        n_samples=1000,      
        n_features=10,       
        n_informative=2,
        n_redundant=8,
        n_classes=2,
        random_state=586
    )
  
    X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(
        X_2, y_2, test_size=0.2, random_state=586
    )
    train_dataset_2 = TensorDataset(torch.FloatTensor(X_train_2), torch.LongTensor(y_train_2))
    test_dataset_2 = TensorDataset(torch.FloatTensor(X_test_2), torch.LongTensor(y_test_2))

    # Create centralized test set
    X_test_cent = np.concatenate([X_test_1, X_test_2])
    y_test_cent = np.concatenate([y_test_1, y_test_2])
    test_dataset_cent = TensorDataset(torch.FloatTensor(X_test_cent), torch.LongTensor(y_test_cent))
    
    # Create return dictionary with all dataloaders
    datasets = {
        "centralized_test": DataLoader(test_dataset_cent, batch_size=32, shuffle=True),
        "client_1_train": DataLoader(train_dataset_1, batch_size=32, shuffle=True),
        "client_1_test": DataLoader(test_dataset_1, batch_size=32, shuffle=True),
        "client_2_train": DataLoader(train_dataset_2, batch_size=32, shuffle=True),
        "client_2_test": DataLoader(test_dataset_2, batch_size=32, shuffle=True),
    }

    return datasets