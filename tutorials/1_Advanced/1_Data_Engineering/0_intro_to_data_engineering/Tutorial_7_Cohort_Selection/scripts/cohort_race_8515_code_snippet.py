import pandas as pd

# In Python Snippet mode the platform auto-loads all inputs into `inputs` —
# a doubly-nested list: inputs[slot_index][dataset_index].
# Each cohort script has one input slot:
#   inputs[0][0] → Patient Features dataset (output of Tutorial 6)

# ---------------------------------------------------------------------------
# Cohort 3: Race concept ID 8515 (OMOP: Asian)
# ---------------------------------------------------------------------------

[[features_df]] = inputs

RACE_CONCEPT_ID = 8515

n_input = len(features_df)
cohort = features_df[
    features_df["race_concept_id"] == RACE_CONCEPT_ID
].copy()

print("Cohort: race_concept_id = {} (OMOP: Asian)".format(RACE_CONCEPT_ID))
print("Input rows:  {}".format(n_input))
print("Output rows: {}".format(len(cohort)))
if len(cohort):
    print("race_concept_id values: {}".format(cohort["race_concept_id"].unique().tolist()))
else:
    print("WARNING: cohort is empty — no patients with race_concept_id={}".format(RACE_CONCEPT_ID))
    print("  Check that race was mapped in Tutorial 4 harmonization.")

outputs = [[cohort]]
