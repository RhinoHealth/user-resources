import sys

from lightning import pytorch as pl
import numpy as np
import pandas as pd
import torch

from chemprop import data, featurizers, models, nn
from chemprop.nn.metrics import (
    MSEMetric,
    MAEMetric,
    R2Metric,
)


class RegressionMPNN(models.MPNN):
    def __init__(
        self,
    ):
        mp = nn.BondMessagePassing()
        agg = nn.MeanAggregation()
        ffn = nn.RegressionFFN()
        mets = [
            MSEMetric(),
            MAEMetric(),
            R2Metric(),
        ]
        super().__init__(mp, agg, ffn, metrics=mets)


def load_data_from_path(filepath, smiles_column, target_columns):
    df = pd.read_csv(filepath)
    smis = df.loc[:, smiles_column].values
    ys = df.loc[:, target_columns].values
    return [data.MoleculeDatapoint.from_smi(smi, y) for smi, y in zip(smis, ys)]


def infer(model_params_file_path):
    # Setup the model
    model = RegressionMPNN()
    model.load_state_dict(torch.load(model_params_file_path)["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"Running inference on {device}")
    model.to(device)

    # Preparing the dataset for testing.
    tabular_data = pd.read_csv("/input/dataset.csv")
    test_data = load_data_from_path("/input/dataset.csv", "smiles", ["molecule_weight"])

    # inference code
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    test_dset = data.MoleculeDataset(test_data, featurizer)
    test_loader = data.build_dataloader(
        test_dset, num_workers=0, shuffle=False, seed=42
    )
    with torch.inference_mode():
        trainer = pl.Trainer(
            logger=None, enable_progress_bar=True, accelerator="cpu", devices=1
        )
        test_preds = trainer.predict(model, test_loader)

    tabular_data["pred_molecule_weight"] = np.concatenate(test_preds, axis=0)
    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    model_params_file_path = sys.argv[1]
    infer(model_params_file_path)
    sys.exit(0)
