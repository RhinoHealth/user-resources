# Tutorial 6 — Feature Engineering

This tutorial derives **patient-level features** from the three validated OMOP datasets produced in Tutorials 4 and 5. The result is a single ML-ready feature table: one row per patient, one column per derived feature.

Feature engineering runs as a **Generalized Compute Code Object** on the Rhino client, using the `generic-python-runner` container. The Python script is passed to the container at run time as a run parameter — not embedded in the Code Object definition — so the same Code Object can be re-run with a different script without re-registration. The script reads **three inputs simultaneously** (OMOP Person, Visit Occurrence, and Procedure Occurrence), joins them on `person_id` entirely on the client, and produces a flat feature table ready for model training.

---

## What You Will Do

1. Define a Python script that reads all three OMOP tables from indexed input paths and pass it to the container at run time via `run_params`
2. Derive age, gender flags, visit counts, procedure counts, and clinical history span per patient
3. Register and run the Code Object on the Rhino client
4. Verify the output with federated analytics (row count, age distribution, visit/procedure summaries)

---

## What Is Feature Engineering?

Raw clinical data — even well-harmonized data in OMOP format — rarely maps directly to what a machine learning model expects as input. **Feature engineering** is the process of transforming raw data fields into a numeric, patient-level representation that a model can train on.

### The Problem: Multi-Table Clinical Data

OMOP structures data relationally: each table captures one entity type.

| Table | Rows | Example |
|---|---|---|
| `person` | 1 row per patient | Patient #42: born 1971, female |
| `visit_occurrence` | 1 row per visit | Patient #42 had 4 visits in 2023 |
| `procedure_occurrence` | 1 row per procedure | Patient #42 had 8 procedures across those visits |

A single patient with 4 visits and 8 procedures spans **13 rows across three tables**. Machine learning models, on the other hand, expect a flat matrix: one row per patient, one column per feature.

### The Solution: Aggregation, Derivation, and Encoding

Feature engineering collapses the multi-table structure into that flat representation through three operations:

**Aggregation** — summarize multiple rows per patient into a single value.
> 4 rows in `visit_occurrence` → `visit_count = 4`
> 8 rows in `procedure_occurrence` → `procedure_count = 8`

**Derivation** — compute new values from existing fields.
> `year_of_birth = 1971` → `age = 53` (as of reference year 2024)
> First visit `2023-01-10`, last visit `2023-11-20` → `days_of_clinical_history = 313`

**Encoding** — convert categorical values to numeric form that a model can use.
> `gender_concept_id = 8507` (OMOP code for Male) → `is_male = 1`, `is_female = 0`

After feature engineering, the 13 rows for Patient #42 become a **single row** with columns like `age`, `visit_count`, `procedure_count`, `is_female`, `has_inpatient_visit`, etc.

### Why the Quality of Features Matters

A poorly designed feature can silently degrade model performance even when the underlying data is correct. For example:

- Passing `gender_concept_id` (an arbitrary integer code like 8507 or 8532) directly to a model that treats all integers as continuous values would mislead the model into treating gender as a numeric scale.
- Using raw `year_of_birth` instead of `age` works, but is less stable — a model trained one year will behave differently the next without retraining, because the same year of birth now maps to a different feature value.

Thoughtful feature engineering is where clinical domain knowledge gets encoded into the representation the model learns from.

---

## UI Alternative: Python Code Snippet

If you prefer not to use the notebook, you can create and run this Code Object directly from the FCP Dashboard. Two approaches are supported:

**Option A — Generalized Compute (matches the notebook)**
1. Dashboard → Code → New Code Object → **Generalized Compute**
2. Select the `generic-python-runner` container image
3. Add 3 inputs, add 1 output (Auto-Generate Schema)
4. Run the Code Object and pass the script as a run parameter (`run_params["code"]`)

**Option B — Python Code Snippet (UI paste-in)**
1. Dashboard → Code → New Code Object → **Python Code** → Code Snippet
2. Select **Python 3.9**, paste the contents of `scripts/feature_engineering_code_snippet.py`
3. Add 3 inputs, add 1 output (Auto-Generate Schema)
4. Click Run

The snippet version uses `[[person_df], [visit_df], [proc_df]] = inputs` and `outputs = [[features]]` — the platform injects DataFrames directly rather than reading from file paths.

---

## Why Run This Inside a Code Object?

This tutorial runs feature engineering as a Rhino Code Object rather than locally in the notebook. The reasons are the same as in Tutorial 3:

- **Data stays on the client.** The join across all three OMOP tables happens locally — no individual patient records are transmitted to the FCP cloud or your notebook.
- **The script is reusable.** Once registered, the same Code Object can be run at any additional participating site with a single API call — no code changes needed.
- **Outputs are tracked.** The feature dataset is registered on the FCP with an auto-inferred schema, giving you a clean audit trail from raw data to model-ready features.

---

## Data Quality and Missing Patients

Real-world data is rarely perfectly consistent across tables. This tutorial's Code Object handles three specific cases gracefully rather than failing silently:

| Issue | Behavior |
|---|---|
| Null `person_id` in the Person table | Row is dropped — no identifier means no feature row can be built |
| Null `year_of_birth` in the Person table | Row is dropped — `age` cannot be derived without it |
| Visit or procedure rows referencing a `person_id` not in the Person table | Row is dropped — the corresponding patient has no demographic context |

In all cases, a warning is recorded and printed in the run logs at the end of the script. This gives you visibility into how many rows were dropped and why, without stopping the run. Patients with no visits or procedures in the cleaned tables are **kept** — they receive zeros for all visit- and procedure-derived features.

You can review the logged warnings from the FCP Dashboard under **Code Runs → [your run] → Logs**.

---

## Features Derived

The feature engineering script produces one row per patient with the following columns:

| Feature | Source Table | Description |
|---|---|---|
| `person_id` | Person | Unique patient identifier |
| `age` | Person | `2024 − year_of_birth` |
| `gender_concept_id` | Person | OMOP standard concept ID for gender |
| `race_concept_id` | Person | OMOP standard concept ID for race |
| `ethnicity_concept_id` | Person | OMOP standard concept ID for ethnicity |
| `is_male` | Person | 1 if `gender_concept_id = 8507`, else 0 |
| `is_female` | Person | 1 if `gender_concept_id = 8532`, else 0 |
| `visit_count` | Visit Occurrence | Total visits recorded for this patient |
| `has_inpatient_visit` | Visit Occurrence | 1 if any inpatient visit (`concept_id = 9201`) |
| `has_outpatient_visit` | Visit Occurrence | 1 if any outpatient visit (`concept_id = 9202`) |
| `has_emergency_visit` | Visit Occurrence | 1 if any emergency visit (`concept_id = 9203`) |
| `days_of_clinical_history` | Visit Occurrence | Days from first to last recorded visit |
| `procedure_count` | Procedure Occurrence | Total procedures recorded for this patient |
| `unique_procedure_count` | Procedure Occurrence | Distinct procedure concept IDs |

---

## How Multi-Input Code Objects Work

Tutorial 3 used Code Objects with a single input dataset — the script read from `/input/dataset.csv`. When a Code Object receives **multiple inputs**, each input is available at an indexed path:

| Input Slot | Path in Container | Dataset |
|---|---|---|
| 0 | `/input/0/dataset.csv` | OMOP Person |
| 1 | `/input/1/dataset.csv` | OMOP Visit Occurrence |
| 2 | `/input/2/dataset.csv` | OMOP Procedure Occurrence |

The slot order is set by the `input_dataset_uids` list when you call `run_code_object`. The script reads each file independently and joins them in memory on the client.

---

## What Is Not Returned

As with all Code Objects, only the output dataset metadata is returned to the FCP cloud. The join, the intermediate DataFrames, and the individual patient records are never transmitted. You receive:

- A registered output dataset (`Patient Features — Site A`) with the derived columns
- An auto-inferred schema describing the feature table structure
- Logs from the Code Object run, including row counts, feature summaries, and any data quality warnings

To inspect individual rows, use an **Interactive Container** on the Rhino client (covered in Tutorial 2).

---

## What Comes Next

The feature table produced here is the starting point for federated model training. You can:

- Pass the feature dataset as input to an NVFlare federated learning container
- Run additional federated analytics (correlations, distributions) across sites using the feature table
- Export schema information to inform downstream pipeline configuration

---

## Checking Your Work in the FCP Dashboard

### Reviewing the Code Object

1. Navigate to **Projects → [Your Project] → Code**
2. Find `Feature Engineering — Patient Features`
3. Click the three-dot menu → **Show code object configuration** to inspect the script and input/output schema assignments

### Reviewing the Run

1. Navigate to **Projects → [Your Project] → Code Runs**
2. Click the most recent run under `Feature Engineering — Patient Features`
3. Verify:
   - Three input datasets listed (Person, Visit Occurrence, Procedure Occurrence)
   - One output dataset listed (`Patient Features — Site A`)
   - Logs show expected row counts, feature summaries, and the data quality warning block at the end

### Reviewing the Output Dataset

1. Navigate to **Projects → [Your Project] → Datasets**
2. Find `Patient Features — Site A`
3. Click → **Analytics** tab to view column distributions
   - `age` distribution should show realistic range (20–80+)
   - `visit_count` histogram should show most patients with 1–3 visits
   - `procedure_count` histogram should reflect the cleaned procedures dataset

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com)
