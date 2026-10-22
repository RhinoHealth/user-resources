"""Split the Kaggle "Chest X-Ray Images (Pneumonia)" archive into one dataset per site, by patient.

Usage: python make_shards.py --archive-dir <unzipped chest_xray folder> [--num-shards 8] [--output-dir .]

Download the archive from https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia and unzip it. It has
`chest_xray/{train,val,test}/{NORMAL,PNEUMONIA}/*.jpeg`. This copies every image into `<output-dir>/images/` under a
unique name and writes `<output-dir>/shards/shard_01.csv` … `shard_NN.csv` with the columns `JPG_file`, `Patient_ID`
and `Pneumonia`. All images of one patient go to the same shard. Import each shard as one site's dataset, with
`<output-dir>/images` as the folder its `JPG_file` names are relative to.
"""

import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

COLUMNS = ["JPG_file", "Patient_ID", "Pneumonia"]
SEED = 42


def main() -> None:
    args = _parse_args()
    images = _list_images(args.archive_dir)
    if images.empty:
        raise SystemExit(f"No .jpeg images found under {args.archive_dir}.")
    patients = images["Patient_ID"].drop_duplicates().sample(frac=1, random_state=SEED).tolist()
    shard_of_patient = {patient: index % args.num_shards + 1 for index, patient in enumerate(patients)}
    images["shard"] = images["Patient_ID"].map(shard_of_patient)

    images_dir, shards_dir = args.output_dir / "images", args.output_dir / "shards"
    images_dir.mkdir(parents=True, exist_ok=True)
    shards_dir.mkdir(parents=True, exist_ok=True)
    for row in images.itertuples():
        target = images_dir / row.JPG_file
        if not target.exists():
            shutil.copy2(row.source_path, target)
    for shard, rows in images.groupby("shard"):
        rows[COLUMNS].to_csv(shards_dir / f"shard_{shard:02d}.csv", index=False)

    summary = images.groupby("shard").agg(
        images=("JPG_file", "size"), patients=("Patient_ID", "nunique"), pneumonia_rate=("Pneumonia", "mean")
    )
    print(f"Wrote {args.num_shards} shards, {len(images)} images, {len(patients)} patients, to {args.output_dir}")
    print(summary.round(3))


def _list_images(archive_dir: Path) -> pd.DataFrame:
    rows = []
    seen = set()
    for image in sorted(archive_dir.rglob("*.jpeg")):
        if "__MACOSX" in image.parts:
            continue
        split, label = image.parent.parent.name, image.parent.name
        jpg_file = f"{split}_{label}_{image.name}"
        # Some copies of the archive contain the whole dataset twice (chest_xray/chest_xray/...).
        if jpg_file in seen:
            continue
        seen.add(jpg_file)
        rows.append(
            {
                "JPG_file": jpg_file,
                "Patient_ID": f"{label}-{_patient_id(label, image.stem)}",
                "Pneumonia": int(label == "PNEUMONIA"),
                "source_path": image,
            }
        )
    return pd.DataFrame(rows)


def _patient_id(label: str, stem: str) -> str:
    """Patient from the file name: `person123_bacteria_456` for pneumonia, `IM-0115-0001` for normal images."""
    if label == "PNEUMONIA":
        match = re.match(r"(person\d+)_", stem)
        return match.group(1) if match else stem
    return re.sub(r"-\d+$", "", stem)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, required=True, help="the unzipped chest_xray folder")
    parser.add_argument("--num-shards", type=int, default=8, help="number of sites")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    return parser.parse_args()


if __name__ == "__main__":
    main()
