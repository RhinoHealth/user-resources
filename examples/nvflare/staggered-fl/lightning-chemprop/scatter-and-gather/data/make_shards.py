"""Split the CYP3A4 inhibition data into one dataset per site.

Usage: python make_shards.py [--num-shards 8] [--output-dir shards]

Reads `examples/site-testing-life-science/data/cyp3a4_all_no_test.csv` from this repository and writes
`shard_01.csv` … `shard_NN.csv` with the columns `id`, `smiles`, `cyp3a4`. Each shard gets the same share of
inhibitors (round-robin within each label). Import each shard as one site's dataset.
"""

import argparse
from pathlib import Path

import pandas as pd

SOURCE_CSV = Path(__file__).resolve().parents[5] / "site-testing-life-science" / "data" / "cyp3a4_all_no_test.csv"
COLUMNS = ["id", "smiles", "cyp3a4"]
SEED = 42


def main() -> None:
    args = _parse_args()
    molecules = pd.read_csv(SOURCE_CSV)[COLUMNS].drop_duplicates("smiles").sample(frac=1, random_state=SEED)
    molecules["shard"] = molecules.groupby("cyp3a4").cumcount() % args.num_shards + 1
    molecules = _drop_one_row_from_sizes_divisible_by_5(molecules)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for shard, rows in molecules.groupby("shard"):
        rows[COLUMNS].to_csv(args.output_dir / f"shard_{shard:02d}.csv", index=False)
    summary = molecules.groupby("shard")["cyp3a4"].agg(molecules="size", inhibitor_rate="mean").round(3)
    print(f"Wrote {args.num_shards} shards, {len(molecules)} molecules, to {args.output_dir}\n{summary}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-shards", type=int, default=8, help="number of sites")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "shards")
    return parser.parse_args()


def _drop_one_row_from_sizes_divisible_by_5(molecules: pd.DataFrame) -> pd.DataFrame:
    """Chemprop's 80/20/0 split leaves the test set empty and fails when the size is a multiple of 5."""
    sizes = molecules["shard"].value_counts()
    first_row_of = [molecules.index[molecules["shard"] == shard][0] for shard in sizes[sizes % 5 == 0].index]
    return molecules.drop(first_row_of)


if __name__ == "__main__":
    main()
