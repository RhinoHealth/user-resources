# You can use this script to create a code object (Python Code Snippet) manually via the UI
# Python Code, Add 3 Inputs, Add 1 Output (Auto-Generate Schema), Use Python 3.9, and paste this entire file's contents under Code Snippet
# Note that Code Snippets expect the variable `outputs` to be a dataframe, so we assign the features dataframe to outputs[0][0] (the first output slot and first dataset index).

import pandas as pd

errors = []

# In Python Snippet mode the platform auto-loads all inputs into `inputs` —
# a doubly-nested list: inputs[slot_index][dataset_index].
# Slot order matches the input list set when creating the code object:
#   inputs[0][0] → OMOP Person
#   inputs[1][0] → OMOP Visit Occurrence
#   inputs[2][0] → OMOP Procedure Occurrence
[[person_df], [visit_df], [proc_df]] = inputs

print("Loaded: person={} rows, visits={} rows, procedures={} rows".format(
    len(person_df), len(visit_df), len(proc_df)
))

# --- Validate Person table ---
n_before = len(person_df)
person_df = person_df[person_df["person_id"].notna()]
if len(person_df) < n_before:
    errors.append("Person: dropped {} row(s) with null person_id".format(n_before - len(person_df)))

n_before = len(person_df)
person_df = person_df[person_df["year_of_birth"].notna()]
if len(person_df) < n_before:
    errors.append("Person: dropped {} row(s) with null year_of_birth - age cannot be derived".format(
        n_before - len(person_df)
    ))

valid_person_ids = set(person_df["person_id"].unique())
print("Valid person IDs after Person table validation: {}".format(len(valid_person_ids)))

# --- Validate Visit Occurrence table ---
n_before = len(visit_df)
visit_df = visit_df[visit_df["person_id"].notna()]
if len(visit_df) < n_before:
    errors.append("Visits: dropped {} row(s) with null person_id".format(n_before - len(visit_df)))

orphaned_visits = ~visit_df["person_id"].isin(valid_person_ids)
if orphaned_visits.sum():
    errors.append("Visits: dropped {} row(s) referencing a person_id not found in the Person table".format(
        orphaned_visits.sum()
    ))
    visit_df = visit_df[~orphaned_visits]

# --- Validate Procedure Occurrence table ---
n_before = len(proc_df)
proc_df = proc_df[proc_df["person_id"].notna()]
if len(proc_df) < n_before:
    errors.append("Procedures: dropped {} row(s) with null person_id".format(n_before - len(proc_df)))

orphaned_procs = ~proc_df["person_id"].isin(valid_person_ids)
if orphaned_procs.sum():
    errors.append("Procedures: dropped {} row(s) referencing a person_id not found in the Person table".format(
        orphaned_procs.sum()
    ))
    proc_df = proc_df[~orphaned_procs]

# --- Patient-level base features (from OMOP Person) ---
features = person_df[["person_id", "year_of_birth", "gender_concept_id",
                       "race_concept_id", "ethnicity_concept_id"]].copy()

REFERENCE_YEAR = 2024
features["age"] = (REFERENCE_YEAR - features["year_of_birth"]).astype(int)

# Cast to int — OMOP IDs may be float64 after harmonization
features["person_id"] = features["person_id"].astype(int)
for col in ["gender_concept_id", "race_concept_id", "ethnicity_concept_id"]:
    features[col] = features[col].fillna(0).astype(int)

features["is_male"]   = (features["gender_concept_id"] == 8507).astype(int)
features["is_female"] = (features["gender_concept_id"] == 8532).astype(int)

# --- Visit-level features ---
visit_agg = visit_df.groupby("person_id").agg(
    visit_count=("visit_occurrence_id", "count"),
    has_inpatient_visit=("visit_concept_id", lambda x: int((x == 9201).any())),
    has_outpatient_visit=("visit_concept_id", lambda x: int((x == 9202).any())),
    has_emergency_visit=("visit_concept_id", lambda x: int((x == 9203).any())),
).reset_index()

visit_df["visit_start_date"] = pd.to_datetime(visit_df["visit_start_date"], errors="coerce")
date_span = visit_df.groupby("person_id")["visit_start_date"].agg(
    lambda x: (x.max() - x.min()).days
).reset_index()
date_span.columns = ["person_id", "days_of_clinical_history"]
visit_agg = visit_agg.merge(date_span, on="person_id", how="left")

# --- Procedure-level features ---
proc_agg = proc_df.groupby("person_id").agg(
    procedure_count=("procedure_occurrence_id", "count"),
    unique_procedure_count=("procedure_concept_id", "nunique"),
).reset_index()

# --- Join ---
features = features.merge(visit_agg, on="person_id", how="left")
features = features.merge(proc_agg, on="person_id", how="left")

int_fill_cols = [
    "visit_count", "has_inpatient_visit", "has_outpatient_visit",
    "has_emergency_visit", "procedure_count", "unique_procedure_count",
    "days_of_clinical_history",
]
for col in int_fill_cols:
    if col in features.columns:
        features[col] = features[col].fillna(0).astype(int)

features = features.drop(columns=["year_of_birth"], errors="ignore")

print("Shape: {} rows x {} columns".format(len(features), len(features.columns)))
print("Age: min={}, max={}, mean={:.1f}".format(
    features["age"].min(), features["age"].max(), features["age"].mean()
))
print("Avg visits per patient: {:.1f}".format(features["visit_count"].mean()))
print("Avg procedures per patient: {:.1f}".format(features["procedure_count"].mean()))

if errors:
    print("DATA QUALITY WARNINGS - {} issue(s) found:".format(len(errors)))
    for i, msg in enumerate(errors, 1):
        print("  [{}] {}".format(i, msg))
else:
    print("No data quality issues detected.")

# In Python Snippet mode the platform reads `outputs` to register result datasets.
# outputs is a dataframe, structured as a doubly-nested list: outputs[slot_index][dataset_index].
outputs = [[features]]
