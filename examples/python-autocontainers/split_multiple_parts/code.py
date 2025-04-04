import os
import json
import pandas as pd
import numpy as np

DEFAULT_NUM_PARTS = 3

print("Starting")

# Read the number of expected parts from the input parameters
try:
    with open('/input/run_params.json') as params_file:
        params_json = json.load(params_file)
except FileNotFoundError:
    num_parts = DEFAULT_NUM_PARTS
else:
    num_parts = params_json.get('num_parts', DEFAULT_NUM_PARTS)
print(f"Got {num_parts=}")

try:
    num_parts = int(num_parts)
except ValueError:
    print(f"Invalid value for num_parts (must be a positive integer): {num_parts}")
    exit(1)

if num_parts < 1:
    print(f"Invalid value for num_parts (must be a positive integer): {num_parts}")
    exit(1)

# Read the input data from /input and split it using np.array_split
df = pd.read_csv('/input/0/dataset.csv')
df_parts = np.array_split(df, num_parts)
print(f"Split dataframe (len={df.shape[0]}) into {num_parts} parts")

# Write the outputs - each one to a different subdirectory under /output/0
for index, part in enumerate(df_parts):
    dirpath = f"/output/0/part_{index}/"
    print(f"Writing output into {dirpath}")
    os.mkdir(dirpath)
    part.to_csv(dirpath + "/dataset.csv", index=False)

print("Done")