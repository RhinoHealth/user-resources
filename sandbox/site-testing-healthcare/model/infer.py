#!/usr/bin/env python
import sys

from lightning import pytorch as pl
import numpy as np
import pandas as pd
import torch

from chemprop import data, featurizers
from chemprop_fl_classification import ClassificationMPNN, load_data_from_path


def infer(model_params_file_path):
    # Setup the model
    model = ClassificationMPNN()
    model.load_state_dict(torch.load(model_params_file_path)["model"])
    model.eval()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # Preparing the dataset for testing.
    tabular_data = pd.read_csv("/input/dataset.csv")
    test_data = load_data_from_path("/input/dataset.csv", "smiles", ["cyp3a4"])

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

    tabular_data["score"] = np.concatenate(test_preds, axis=0)
    tabular_data.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
