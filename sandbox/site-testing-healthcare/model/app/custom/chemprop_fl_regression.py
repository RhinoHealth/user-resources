import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
from pathlib import Path

from chemprop import data, featurizers, models, nn
from chemprop.nn.metrics import (
    R2Metric,
    MSEMetric,
    MAEMetric,
)
from lightning import pytorch as pl
import pandas as pd

# (1) import nvflare lightning client API
import nvflare.client.lightning as flare

pl.seed_everything(42, workers=True)


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


def _load_data_from_path(filepath, smiles_column, target_columns):
    df = pd.read_csv(filepath)
    smis = df.loc[:, smiles_column].values
    ys = df.loc[:, target_columns].values
    return [data.MoleculeDatapoint.from_smi(smi, y) for smi, y in zip(smis, ys)]


def _get_train_validation_split(input_data, split=(0.79, 0.2, 0.01)):
    mols = [
        d.mol for d in input_data
    ]  # RDkit Mol objects are use for structure based splits
    train_indices, val_indices, test_indices = data.make_split_indices(
        mols, "random", split
    )
    train_data, val_data, _ = data.split_data_by_indices(
        input_data, train_indices, val_indices, test_indices
    )
    return train_data, val_data


def _get_model_and_loaders(datapath):
    # input data needs to be split in train/validation for the chemprop algorithm
    input_data = _load_data_from_path(datapath, "smiles", ["normalized"])
    train_data, val_data = _get_train_validation_split(input_data)

    # create features from data
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    train_dset = data.MoleculeDataset(train_data, featurizer)
    val_dset = data.MoleculeDataset(val_data, featurizer)

    # instantiate data loaders
    train_loader = data.build_dataloader(train_dset, num_workers=0, seed=42)
    val_loader = data.build_dataloader(val_dset, num_workers=0, shuffle=False, seed=42)

    mpnn = RegressionMPNN()

    return mpnn, train_loader, val_loader


def main():
    dataset_dirs = [
        x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()
    ]
    DATASET_PATH = Path(dataset_dirs[0] / "dataset.csv")
    mpnn, train_loader, val_loader = _get_model_and_loaders(DATASET_PATH)

    trainer = pl.Trainer(
        logger=False,
        enable_checkpointing=True,  # Use `True` if you want to save model checkpoints. The checkpoints will be saved in the `checkpoints` folder.
        enable_progress_bar=True,
        accelerator="auto",
        devices=1,
        max_epochs=20,  # number of epochs to train for
        deterministic=True,
    )

    # (2) patch the lightning trainer
    flare.patch(trainer)

    while flare.is_running():
        # (3) receives FLModel from NVFlare
        # Note that we don't need to pass this input_model to trainer
        # because after flare.patch the trainer.fit/validate will get the
        # global model internally
        input_model = flare.receive()
        print(f"current_round={input_model.current_round}")

        # (4) evaluate the current global model to allow server-side model selection
        print("--- validate global model ---")
        trainer.validate(mpnn, dataloaders=val_loader)

        # perform local training
        print("--- train new model ---")
        trainer.fit(mpnn, train_loader, val_loader)


if __name__ == "__main__":
    main()
