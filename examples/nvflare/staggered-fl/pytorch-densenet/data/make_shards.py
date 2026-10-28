"""Split part of the Kaggle "Chest X-Ray Images (Pneumonia)" archive into one dataset per site, by patient.

Usage: python make_shards.py --archive <archive.zip or unzipped folder> [--num-shards 8] [--images-per-site 150]
                             [--output-dir .]

Download the archive from https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia; there is no need to
unzip it. It has `chest_xray/{train,val,test}/{NORMAL,PNEUMONIA}/*.jpeg` (plus a duplicate copy and `__MACOSX`, both
skipped). This takes about `--images-per-site` images for each site, copies them into `<output-dir>/images/` under
unique names, and writes `<output-dir>/shards/shard_01.csv` … `shard_NN.csv` with the columns `JPG_file`,
`Patient_ID` and `Pneumonia`. All images of one patient go to the same shard. Import each shard as one site's
dataset, with `<output-dir>/images` as the folder its `JPG_file` names are relative to.
"""

import argparse
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath

import pandas as pd

COLUMNS = ["JPG_file", "Patient_ID", "Pneumonia"]
SEED = 42


def main() -> None:
    args = _parse_args()
    images = _list_images(args.archive)
    if images.empty:
        raise SystemExit(f"No .jpeg images found in {args.archive}.")
    patients = images["Patient_ID"].drop_duplicates().sample(frac=1, random_state=SEED).tolist()
    shard_of_patient = {patient: index % args.num_shards + 1 for index, patient in enumerate(patients)}
    images["shard"] = images["Patient_ID"].map(shard_of_patient)
    if args.images_per_site:
        images = _limit_images_per_shard(images, patients, args.images_per_site)

    images_dir, shards_dir = args.output_dir / "images", args.output_dir / "shards"
    images_dir.mkdir(parents=True, exist_ok=True)
    shards_dir.mkdir(parents=True, exist_ok=True)
    _copy_images(args.archive, images, images_dir)
    for shard, rows in images.groupby("shard"):
        rows[COLUMNS].to_csv(shards_dir / f"shard_{shard:02d}.csv", index=False)

    summary = images.groupby("shard").agg(
        images=("JPG_file", "size"), patients=("Patient_ID", "nunique"), pneumonia_rate=("Pneumonia", "mean")
    )
    print(f"Wrote {args.num_shards} shards, {len(images)} images, to {args.output_dir}")
    print(summary.round(3))


def _list_images(archive: Path) -> pd.DataFrame:
    """One row per unique image, with `source` the image's path in the folder or its member name in the zip."""
    if archive.is_dir():
        sources = [str(path.relative_to(archive)) for path in archive.rglob("*.jpeg")]
    else:
        with zipfile.ZipFile(archive) as zip_file:
            sources = [name for name in zip_file.namelist() if name.endswith(".jpeg")]

    rows = []
    seen = set()
    for source in sorted(sources):
        path = PurePosixPath(source)
        if "__MACOSX" in path.parts:
            continue
        split, label = path.parent.parent.name, path.parent.name
        jpg_file = f"{split}_{label}_{path.name}"
        # The archive contains the whole dataset twice (chest_xray/chest_xray/...).
        if jpg_file in seen:
            continue
        seen.add(jpg_file)
        rows.append(
            {
                "JPG_file": jpg_file,
                "Patient_ID": f"{label}-{_patient_id(label, path.stem)}",
                "Pneumonia": int(label == "PNEUMONIA"),
                "source": source,
            }
        )
    return pd.DataFrame(rows)


def _limit_images_per_shard(images: pd.DataFrame, patients: list[str], limit: int) -> pd.DataFrame:
    """Keep whole patients, in shuffled order, until each shard has about `limit` images."""
    per_patient = images.groupby("Patient_ID").agg(shard=("shard", "first"), count=("JPG_file", "size"))
    per_patient = per_patient.loc[patients]
    images_before = per_patient.groupby("shard")["count"].cumsum() - per_patient["count"]
    return images[images["Patient_ID"].isin(per_patient.index[images_before < limit])]


def _copy_images(archive: Path, images: pd.DataFrame, images_dir: Path) -> None:
    targets = {row.source: images_dir / row.JPG_file for row in images.itertuples()}
    if archive.is_dir():
        for source, target in targets.items():
            if not target.exists():
                shutil.copy2(archive / source, target)
        return
    with zipfile.ZipFile(archive) as zip_file:
        for source, target in targets.items():
            if not target.exists():
                with zip_file.open(source) as image, open(target, "wb") as copy:
                    shutil.copyfileobj(image, copy)


def _patient_id(label: str, stem: str) -> str:
    """Patient from the file name: `person123_bacteria_456` for pneumonia, `IM-0115-0001` for normal images."""
    if label == "PNEUMONIA":
        match = re.match(r"(person\d+)_", stem)
        return match.group(1) if match else stem
    return re.sub(r"-\d+$", "", stem)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True, help="the downloaded .zip, or the folder it unzips to")
    parser.add_argument("--num-shards", type=int, default=8, help="number of sites")
    parser.add_argument(
        "--images-per-site", type=int, default=150, help="about this many images per site; 0 uses all 5,856 images"
    )
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    return parser.parse_args()


if __name__ == "__main__":
    main()
