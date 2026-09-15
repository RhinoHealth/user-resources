#!/usr/bin/env python
import csv
import os
import sys
from pathlib import Path

import numpy as np


def infer(model_params_file_path):
    # Setup the model
    model = np.load(model_params_file_path)

    # Preparing the dataset for testing.
    with (Path("/input") / "dataset.csv").open("r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        fieldnames = csv_reader.fieldnames
        rows = list(csv_reader)

    # Inference: Apply model and add scores column.
    scores = [1 for row in rows]
    for row, score in zip(rows, scores):
        row["SCORE"] = score

    with (Path("/output") / "dataset.csv").open("w", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=[*fieldnames, "SCORE"])
        csv_writer.writeheader()
        csv_writer.writerows(rows)


if __name__ == "__main__":
    args = sys.argv[1:]
    (model_params_file_path,) = args
    infer(model_params_file_path)
    sys.exit(0)
