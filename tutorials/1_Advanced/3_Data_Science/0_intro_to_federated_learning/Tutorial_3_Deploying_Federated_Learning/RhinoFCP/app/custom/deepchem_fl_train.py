from config import *
import torch
import deepchem as dc
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score

# (1) Import the NVFlare client
import nvflare.client as flare

# Set a random seed for reproducibility
torch.manual_seed(42)

class ClassificationModel(torch.nn.Module):
    def __init__(self, input_features=INPUT_FEATURE_SIZE):
        super(ClassificationModel, self).__init__()
        self.dense1 = torch.nn.Linear(input_features, 1000)
        self.dense2 = torch.nn.Linear(1000, 1)

    def forward(self, inputs):
        y = torch.nn.functional.relu(self.dense1(inputs))
        y = torch.nn.functional.dropout(y, p=0.5, training=self.training)
        logits = self.dense2(y)
        output = torch.sigmoid(logits)
        return output, logits


def load_data(df):
    X = df.loc[:, FEATURE_COLUMNS].values.astype(np.float32)
    y = df.loc[:, TARGET_COLUMN].values.astype(np.float32).reshape(-1, 1)
    ids = df.loc[:, SMILES_ID_COLUMN].values
    dataset = dc.data.NumpyDataset(X=X, y=y, ids=ids)

    print(f"Dataset(s) loaded: {len(dataset)} examples, {dataset.X.shape[1]} features.")
    return dataset

def split_data(full_dataset, frac_train=0.8, frac_valid=0.2, seed=42):
    splitter = dc.splits.RandomSplitter()
    train_dataset, valid_dataset, _ = splitter.train_valid_test_split(
        full_dataset,
        frac_train=frac_train,
        frac_valid=frac_valid,
        frac_test=0.0,
        seed=seed
    )

    if len(train_dataset) == 0 or len(valid_dataset) == 0:
        raise ValueError("Dataset splitting resulted in empty training or validation set.")

    return train_dataset, valid_dataset

def main():
    # (2) Initialize the NVFlare client
    flare.init()

    # Load datasets
    data_dirs = [x for x in TRAIN_DATA_DIR.iterdir() if x.resolve().is_dir()]
    dataset = pd.concat([pd.read_csv(_dataset / "dataset.csv") for _dataset in data_dirs])
    
    print("\nLoaded the following dataset(s):")
    for data_dir in data_dirs:
        print(data_dir)
    full_dataset = load_data(dataset)
    train_dataset, valid_dataset = split_data(full_dataset)

    # Define PyTorch Model and DeepChem TorchModel wrapper
    torch_model = ClassificationModel()
    output_types = ['prediction', 'loss']
    model = dc.models.TorchModel(
        torch_model,
        dc.models.losses.SigmoidCrossEntropy(),
        output_types=output_types
    )
    metric = dc.metrics.Metric(roc_auc_score)

    # Train the model
    print("\n--- Starting Training ---")
    # (3) Federated learning loop
    while flare.is_running():
        # (4) Receive global model from server
        global_model = flare.receive()
        
        # (5) Update local model with global weights
        model.model.load_state_dict(global_model.params)

        # (6) Evaluate global model on local data
        train_score = model.evaluate(train_dataset, [metric])
        valid_score = model.evaluate(valid_dataset, [metric])
        
        # (7) Train for three epoch on local data
        model.fit(train_dataset, nb_epoch=3)

        # (8) Package updated model and metrics
        output_model = flare.FLModel(
            params=model.model.state_dict(),
            metrics={"global_AUC": valid_score['roc_auc_score']}
        )

        # (9) Send updated model back to server
        flare.send(output_model)
        
    print("--- Training Complete ---\n")
    print('\nTraining set score (ROC-AUC):', train_score)
    print('Validation set score (ROC-AUC):', valid_score)


if __name__ == '__main__':
    main()
