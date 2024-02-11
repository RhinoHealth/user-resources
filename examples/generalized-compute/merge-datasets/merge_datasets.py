import pandas as pd

if __name__ == "__main__":
    first = pd.read_csv("/input/0/dataset.csv")
    second = pd.read_csv("/input/1/dataset.csv")
    merged = pd.concat([first, second], ignore_index=True, axis=0)
    merged.to_csv("/output/0/dataset.csv", index=False)
