import os
import pandas as pd

if __name__ == "__main__":
    # Assume that all datasets are under /input/0 as multiple inputs, meaning that each of these datasets is
    # represented by a subdirectory under /input/0 (e.g. /input/0/abcdef-123456/dataset.csv)
    input_dirs = [f.path for f in os.scandir("/input/0") if f.is_dir() and os.path.isfile(f.path + "/dataset.csv")]
    print(f"Found {len(input_dirs)} directories under /input/0: {input_dirs}")

    input_dfs = []
    for input_dir in input_dirs:
        input_df = pd.read_csv(input_dir + "/dataset.csv")
        input_dfs.append(input_df)
    print(f"Going to merge {len(input_dfs)} datasets")

    if input_dirs:
        merged = pd.concat(input_dfs, ignore_index=True, axis=0)
        merged.to_csv("/output/0/dataset.csv", index=False)
    else:
        print("No inputs found...")

    print("Done")
