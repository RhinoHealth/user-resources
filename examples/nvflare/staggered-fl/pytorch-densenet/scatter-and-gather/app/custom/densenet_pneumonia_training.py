"""Federated DenseNet-121 (plain PyTorch) training of a pneumonia classifier from chest X-ray images.

Lines marked `# Staggering:` are what makes this script work with StaggeredScatterAndGather; everything else is a
regular NVFlare Client API script.
"""

import argparse
import gc
import random
from pathlib import Path

import nvflare.client as flare
import pandas as pd
import torch
from network import DenseNetPneumonia
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

DATASETS_DIR = Path("/input/datasets")
DATASET_FILE_NAME = "dataset.csv"
IMAGES_DIR_NAME = "file_data"
IMAGE_COLUMN = "JPG_file"
TARGET_COLUMN = "Pneumonia"
PATIENT_COLUMN = "Patient_ID"
VALIDATION_FRACTION = 0.2
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
SEED = 42


class ChestXRayDataset(Dataset):
    """Chest X-ray images with a 0/1 pneumonia label."""

    def __init__(self, paths: list[Path], labels: list[int], transform: transforms.Compose):
        self.paths = paths
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        image = Image.open(self.paths[index]).convert("RGB")
        return self.transform(image), self.labels[index]


def main() -> None:
    args = _parse_args()
    torch.manual_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_dataset, val_dataset = _build_datasets(_find_dataset_dir(), args.image_size)
    print(f"{len(train_dataset)} training and {len(val_dataset)} validation images, training on {device}.")

    flare.init()
    # Staggering: the in-process client runs this script once for the whole job (config_fed_client.json). Between
    # its turns the site waits here in flare.receive() while other sites train.
    while flare.is_running():
        input_model = flare.receive()
        print(f"Round {input_model.current_round}: validating the global model, then training locally.")
        try:
            output_model = _run_round(input_model, train_dataset, val_dataset, device, args)
        except torch.cuda.OutOfMemoryError:
            print(
                "CUDA out of memory: too many sites train on this GPU at once. Lower max_concurrent in "
                "config_fed_server.json, or lower --batch-size.",
                flush=True,
            )
            raise
        flare.send(output_model)


def _run_round(
    input_model: flare.FLModel,
    train_dataset: ChestXRayDataset,
    val_dataset: ChestXRayDataset,
    device: torch.device,
    args: argparse.Namespace,
) -> flare.FLModel:
    """Validate the global model, train it for one round and return the local model, leaving nothing on the GPU."""
    model = DenseNetPneumonia(pretrained=False)
    model.load_state_dict(input_model.params)
    model.to(device)
    # Validating the received global model lets the server pick the best global model.
    metrics = _validate(model, val_dataset, device, args)
    print(f"Global model: {metrics}")
    _train(model, train_dataset, device, args)
    params = {name: value.detach().cpu() for name, value in model.state_dict().items()}

    # Staggering: this script outlives the round, so free the model and PyTorch's cached GPU memory before the site
    # waits for its next turn. A waiting site then holds only its CUDA context (~0.3 GB) instead of its training
    # footprint (~2.7 GB here). The optimizer and data loaders are local to _train and _validate, so they are gone.
    del model
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return flare.FLModel(params=params, metrics=metrics, meta={"NUM_STEPS_CURRENT_ROUND": args.local_steps})


def _train(model: DenseNetPneumonia, dataset: ChestXRayDataset, device: torch.device, args: argparse.Namespace) -> None:
    model.train()
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = torch.nn.CrossEntropyLoss()
    use_amp = _use_amp(device, args)
    scaler = torch.amp.GradScaler(enabled=use_amp)

    step = 0
    loss = torch.tensor(float("nan"))
    while step < args.local_steps:
        for images, labels in loader:
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, enabled=use_amp):
                loss = criterion(model(images), labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            step += 1
            if step == args.local_steps:
                break
    print(f"Trained {step} steps, last loss {loss.item():.4f}.")


@torch.no_grad()
def _validate(
    model: DenseNetPneumonia, dataset: ChestXRayDataset, device: torch.device, args: argparse.Namespace
) -> dict[str, float]:
    model.eval()
    loader = DataLoader(
        dataset, batch_size=args.batch_size, num_workers=args.num_workers, pin_memory=device.type == "cuda"
    )
    scores, labels = [], []
    for images, targets in loader:
        with torch.autocast(device_type=device.type, enabled=_use_amp(device, args)):
            logits = model(images.to(device, non_blocking=True))
        scores.append(logits.float().softmax(dim=1)[:, 1].cpu())
        labels.append(targets)
    scores, labels = torch.cat(scores), torch.cat(labels)
    accuracy = ((scores >= 0.5).long() == labels).float().mean().item()
    return {"val_accuracy": accuracy, "val_auroc": _auroc(scores, labels)}


def _auroc(scores: torch.Tensor, labels: torch.Tensor) -> float:
    """Area under the ROC curve: the chance that a random positive scores above a random negative, ties counting half."""
    positives, negatives = scores[labels == 1], scores[labels == 0]
    if len(positives) == 0 or len(negatives) == 0:
        return float("nan")
    higher = (positives[:, None] > negatives[None, :]).float().mean()
    ties = (positives[:, None] == negatives[None, :]).float().mean()
    return (higher + 0.5 * ties).item()


def _use_amp(device: torch.device, args: argparse.Namespace) -> bool:
    return device.type == "cuda" and not args.no_amp


def _build_datasets(dataset_dir: Path, image_size: int) -> tuple[ChestXRayDataset, ChestXRayDataset]:
    table = pd.read_csv(dataset_dir / DATASET_FILE_NAME)
    missing = {IMAGE_COLUMN, TARGET_COLUMN, PATIENT_COLUMN} - set(table.columns)
    if missing:
        raise RuntimeError(f"{dataset_dir} is missing column(s) {sorted(missing)}; found {list(table.columns)}.")
    if table.empty:
        raise RuntimeError(f"{dataset_dir / DATASET_FILE_NAME} has no rows.")

    # Split by patient, so no patient has images in both the training and the validation set.
    patients = sorted(table[PATIENT_COLUMN].unique())
    random.Random(SEED).shuffle(patients)
    val_patients = set(patients[: max(1, round(len(patients) * VALIDATION_FRACTION))])
    is_val = table[PATIENT_COLUMN].isin(val_patients)

    normalize = transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)
    train_transform = transforms.Compose(
        [
            transforms.Resize(image_size + 32),
            transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            transforms.ToTensor(),
            normalize,
        ]
    )
    val_transform = transforms.Compose(
        [transforms.Resize(image_size + 32), transforms.CenterCrop(image_size), transforms.ToTensor(), normalize]
    )
    return (
        _dataset(dataset_dir, table[~is_val], train_transform),
        _dataset(dataset_dir, table[is_val], val_transform),
    )


def _dataset(dataset_dir: Path, rows: pd.DataFrame, transform: transforms.Compose) -> ChestXRayDataset:
    paths = [dataset_dir / IMAGES_DIR_NAME / name for name in rows[IMAGE_COLUMN]]
    return ChestXRayDataset(paths, rows[TARGET_COLUMN].astype(int).tolist(), transform)


def _find_dataset_dir() -> Path:
    dataset_dirs = sorted(path for path in DATASETS_DIR.iterdir() if path.is_dir()) if DATASETS_DIR.is_dir() else []
    if len(dataset_dirs) != 1:
        raise RuntimeError(
            f"Expected exactly one dataset under {DATASETS_DIR}, found {len(dataset_dirs)}. Run the job with one "
            f"dataset per site."
        )
    return dataset_dirs[0]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-steps", type=int, default=200, help="training steps (batches) in each FL round")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--num-workers", type=int, default=4, help="data loader worker processes")
    parser.add_argument("--no-amp", action="store_true", help="train in full precision instead of mixed precision")
    return parser.parse_args()


if __name__ == "__main__":
    # Staggering: let errors propagate. The in-process client reports them to the server at once, so the site is
    # excluded within seconds; ending the process here (os._exit) would only be noticed at train_timeout.
    main()
