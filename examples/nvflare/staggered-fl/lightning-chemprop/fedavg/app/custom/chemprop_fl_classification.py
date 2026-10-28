"""Federated Chemprop (PyTorch Lightning) training of a CYP3A4 inhibition classifier from SMILES strings.

Lines marked `# Staggering:` are what makes this script work with StaggeredFedAvg; everything else is a regular
NVFlare Lightning client.
"""

import argparse
from pathlib import Path

import nvflare.client.lightning as flare
import pandas as pd
import torch
from chemprop import data, featurizers, models, nn
from chemprop.nn.metrics import BCEMetric, BinaryAccuracyMetric, BinaryAUPRCMetric, BinaryAUROCMetric
from lightning import pytorch as pl
from torch.utils.data import DataLoader

DATASETS_DIR = Path("/input/datasets")
DATASET_FILE_NAME = "dataset.csv"
SMILES_COLUMN = "smiles"
TARGET_COLUMN = "cyp3a4"
TRAIN_VALIDATION_SPLIT = (0.8, 0.2, 0.0)
SEED = 42


class ClassificationMPNN(models.MPNN):
    """Chemprop message-passing network with a binary classification head."""

    def __init__(self):
        metrics = [BCEMetric(), BinaryAUROCMetric(), BinaryAUPRCMetric(), BinaryAccuracyMetric()]
        super().__init__(
            nn.BondMessagePassing(), nn.MeanAggregation(), nn.BinaryClassificationFFN(), metrics=metrics
        )


def main() -> None:
    args = _parse_args()
    pl.seed_everything(SEED, workers=True)
    train_loader, val_loader = _build_loaders(_find_dataset(), args)
    model = ClassificationMPNN()
    trainer = pl.Trainer(
        logger=False,
        # The server persists the global model every round; local checkpoints would only pile up in the container.
        enable_checkpointing=False,
        enable_progress_bar=False,
        accelerator="auto",
        devices=1,
        # The NVFlare patch raises this by one round's worth each round, since Lightning counts epochs across rounds.
        max_epochs=args.epochs_per_round,
        deterministic=True,
    )
    # Patching makes trainer.fit/validate receive the global model and send the result back to the server.
    flare.patch(trainer)

    # Staggering: the in-process client runs this script once for the whole job (config_fed_client.json). Between
    # its turns the site waits here in flare.receive(), keeping its optimizer, LR schedule and epoch count. No GPU
    # cleanup is needed: NVFlare's Lightning patch moves the model to the CPU after each round, so a waiting site
    # holds only its CUDA context (~0.3 GB) while other sites train.
    while flare.is_running():
        input_model = flare.receive()
        print(f"Round {input_model.current_round}: validating the global model, then training locally.")
        # Validating the received global model lets the server pick the best global model.
        trainer.validate(model, dataloaders=val_loader)
        try:
            trainer.fit(model, train_loader, val_loader)
        except torch.cuda.OutOfMemoryError:
            print(
                "CUDA out of memory: too many sites train on this GPU at once. Lower max_concurrent in "
                "config_fed_server.json, or lower --batch-size.",
                flush=True,
            )
            raise


def _build_loaders(dataset_path: Path, args: argparse.Namespace) -> tuple[DataLoader, DataLoader]:
    table = pd.read_csv(dataset_path)
    missing = {SMILES_COLUMN, TARGET_COLUMN} - set(table.columns)
    if missing:
        raise RuntimeError(f"{dataset_path} is missing column(s) {sorted(missing)}; found {list(table.columns)}.")
    points = [
        data.MoleculeDatapoint.from_smi(smiles, [target])
        for smiles, target in zip(table[SMILES_COLUMN], table[TARGET_COLUMN])
    ]
    train_indices, val_indices, test_indices = data.make_split_indices(
        [point.mol for point in points], "random", TRAIN_VALIDATION_SPLIT
    )
    train_points, val_points, _ = data.split_data_by_indices(points, train_indices, val_indices, test_indices)
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    train_loader = data.build_dataloader(
        data.MoleculeDataset(train_points, featurizer),
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        seed=SEED,
        class_balance=True,
    )
    val_loader = data.build_dataloader(
        data.MoleculeDataset(val_points, featurizer),
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        shuffle=False,
        seed=SEED,
    )
    return train_loader, val_loader


def _find_dataset() -> Path:
    dataset_dirs = sorted(path for path in DATASETS_DIR.iterdir() if path.is_dir()) if DATASETS_DIR.is_dir() else []
    if len(dataset_dirs) != 1:
        raise RuntimeError(
            f"Expected exactly one dataset under {DATASETS_DIR}, found {len(dataset_dirs)}. Run the job with one "
            f"dataset per site."
        )
    return dataset_dirs[0] / DATASET_FILE_NAME


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs-per-round", type=int, default=50, help="local epochs in each FL round")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--num-workers", type=int, default=0, help="data loader worker processes")
    return parser.parse_args()


if __name__ == "__main__":
    # Staggering: let errors propagate. The in-process client reports them to the server at once, so the site is
    # excluded within seconds; ending the process here (os._exit) would only be noticed at train_timeout.
    main()
