import pandas as pd

# In Python Snippet mode the platform auto-loads all inputs into `inputs` —
# a doubly-nested list: inputs[slot_index][dataset_index].
# Each cohort script has one input slot:
#   inputs[0][0] → Patient Features dataset (output of Tutorial 6)

# ---------------------------------------------------------------------------
# Cohort 2: Females aged 30–40
# ---------------------------------------------------------------------------

[[features_df]] = inputs

n_input = len(features_df)
cohort = features_df[
    (features_df["age"] >= 30) &
    (features_df["age"] <= 40) &
    (features_df["is_female"] == 1)
].copy()

print("Cohort: Females aged 30-40")
print("Input rows:  {}".format(n_input))
print("Output rows: {}".format(len(cohort)))
if len(cohort):
    print("Age range: {}-{}".format(cohort["age"].min(), cohort["age"].max()))
    print("is_female values: {}".format(cohort["is_female"].unique().tolist()))
else:
    print("WARNING: cohort is empty — check that the feature table contains age and is_female columns")

outputs = [[cohort]]