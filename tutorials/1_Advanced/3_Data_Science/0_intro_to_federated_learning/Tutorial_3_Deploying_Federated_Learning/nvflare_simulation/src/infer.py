from config import *
import sys
import torch
import deepchem as dc
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score

# DeepChem Model
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


def load_data(filepath):
    print(f"Loading data from {filepath}...")

    df = pd.read_csv(filepath)
    X = df.loc[:, FEATURE_COLUMNS].values.astype(np.float32)
    y = df.loc[:, TARGET_COLUMN].values.astype(np.float32).reshape(-1, 1)
    ids = df.loc[:, SMILES_ID_COLUMN].values
    dataset = dc.data.NumpyDataset(X=X, y=y, ids=ids)

    print(f"Dataset loaded: {len(dataset)} examples, {dataset.X.shape[1]} features.")
    return dataset, df


def infer(model_params_file_path: str, input_data_file_path: str, output_file_path: str):
    # Define PyTorch Model and DeepChem TorchModel wrapper
    torch_model = ClassificationModel()
    output_types = ['prediction', 'loss']
    model = dc.models.TorchModel(
        torch_model,
        dc.models.losses.SigmoidCrossEntropy(),
        output_types=output_types
    )

    # Load Weights
    print(f"Loading model parameters from: {model_params_file_path}")
    model.model.load_state_dict(torch.load(model_params_file_path)["model"])
    
    # Define metric (roc auc)
    metric = dc.metrics.Metric(roc_auc_score)

    # Load Input Data
    test_dataset, input_df = load_data(input_data_file_path)

    # Evaluate and predict
    test_score = model.evaluate(test_dataset, [metric])
    test_preds = model.predict(test_dataset)
    
    # Save Results
    input_df["pred"] = test_preds
    output_df = input_df[["ids", "w", "y", "pred"]].copy()
    output_df.to_csv(output_file_path, index=False)

    print(f"\nInference complete. Predictions saved to {output_file_path}")
    print('\nTest set score (ROC-AUC):', test_score)


if __name__ == "__main__":
    # Ensure Output directory Exists
    PREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    infer(
        model_params_file_path=MODEL_PARAMS_PATH,
        input_data_file_path=TEST_DATA_PATH,
        output_file_path=PREDS_PATH
    )
    sys.exit(0)

