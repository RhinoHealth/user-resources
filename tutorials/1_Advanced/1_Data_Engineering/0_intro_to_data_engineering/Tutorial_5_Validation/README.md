# Tutorial 5 — OMOP Validation

This tutorial verifies that the harmonized datasets produced in Tutorial 4 actually conform to the OMOP Common Data Model standard. It is your quality assurance step — run it before using the harmonized data in any analysis or model training.

---

## What You Will Do

1. Check that all required OMOP columns are present in each output table
2. Verify that key fields have no null values where OMOP requires them
3. Confirm that all concept IDs use recognized OMOP vocabulary values
4. Measure how much of your data was successfully mapped (coverage)
5. Check referential integrity — that IDs linking the three tables are consistent
6. Receive a final pass/warn/fail summary with recommended next steps

---

## Why Validation Matters

Harmonization is an automated process, and automated processes can produce subtle errors without announcing them:

- A CPT code in the source data that was not included in your semantic mapping will produce a `procedure_concept_id` of zero — the record is technically present, but clinically useless for OMOP-based analysis
- A patient with an unexpected `Gender` value (e.g. `"Unk"` at one site, `"Unknown"` at another) will have a null `gender_concept_id` — violating OMOP requirements for that field
- A date stored in the wrong format silently fails to parse, leaving a null where a valid date should be

**Running validation before using your data:**
- Catches these errors before they propagate into research outputs
- Creates a documented audit trail that the data meets the standard (often required for publication or IRB reporting)
- Identifies gaps in your semantic mappings that should be closed before scaling to additional sites

---

## What OMOP Requires

### OMOP Person Table

The `person` table must have one row per unique patient. Key rules:

| Column | Requirement |
|---|---|
| `person_id` | Non-null, unique integer for every patient |
| `gender_concept_id` | Must be a valid OMOP gender concept ID (or 0 for unknown) |
| `race_concept_id` | Must be a valid OMOP race concept ID (or 0) |
| `ethnicity_concept_id` | Must be a valid OMOP ethnicity concept ID (or 0) |
| `year_of_birth` | Non-null integer |

### OMOP Visit Occurrence Table

| Column | Requirement |
|---|---|
| `visit_occurrence_id` | Non-null, unique per visit |
| `person_id` | Must reference a real patient |
| `visit_concept_id` | Valid OMOP visit type concept (Inpatient/Outpatient/Emergency or 0) |
| `visit_start_date` | Non-null, valid date |

### OMOP Procedure Occurrence Table

| Column | Requirement |
|---|---|
| `procedure_occurrence_id` | Non-null, unique per procedure |
| `person_id` | Must reference a real patient |
| `visit_occurrence_id` | Must reference a real visit |
| `procedure_concept_id` | Valid OMOP concept (from CPT mapping, or 0 for unmapped) |
| `procedure_date` | Non-null, valid date |

---

## What Is Concept ID = 0?

In OMOP CDM, `concept_id = 0` is the standard way to represent *"no matching standard concept was found."* It is technically valid — OMOP allows it — but it means that record will be excluded from any analysis that filters for standard concepts (which is most OMOP-based queries).

A `concept_id = 0` in your harmonized data can mean:
1. The source value was not included in your semantic mapping (most common)
2. The source value could not be matched to any standard vocabulary term
3. The source field was null before harmonization

This tutorial flags any `concept_id = 0` rate above 20% as a warning. If you see high rates, return to Tutorial 4 and add the missing source values to the appropriate semantic mapping, then re-run.

---

## How Validation Works on Federated Data

Because raw data never leaves the site, validation checks run as **federated metrics and SQL queries** — the same mechanism used in Tutorial 2. You receive aggregate counts and rates, not individual rows. This means:

- You can confirm *how many* records have a null `person_id`, but not *which* records
- You can see *what percentage* of procedures mapped to concept_id = 0, but not *which* procedures
- If you need to investigate specific failing records, use an **Interactive Container** (covered in Tutorial 2) to inspect the harmonized output file directly on the server

---

## Understanding Validation Results

| Result | Meaning | What To Do |
|---|---|---|
| ✅ PASS | Check passed with no issues | Nothing — proceed |
| ⚠️ WARN | Potential issue — data is usable but may have gaps | Investigate before using in analysis |
| ❌ FAIL | Critical issue — data does not meet OMOP standard | Must be fixed before use |

Any FAIL result should be traced back to Tutorial 4:

1. Open the harmonized dataset in the FCP Dashboard under **Projects → Datasets**
2. Navigate to **Projects → Harmonization** to inspect the semantic or syntactic mapping that caused the issue
3. Correct the mapping (add missing terms, fix wrong concept IDs)
4. Re-run the harmonization (Tutorial 4 run cells)
5. Re-run this validation notebook

---

## Checking Your Work in the FCP Dashboard

### Reviewing Harmonized Datasets
1. Navigate to **Projects → [Your Project] → Datasets**
2. The three OMOP output datasets will be listed: `OMOP Person`, `OMOP Visit Occurrence`, `OMOP Procedure Occurrence`
3. Click each one and use the **Analytics** tab to view column distributions — cross-check concept ID distributions with the notebook output

### Reviewing the Harmonization Mapping
1. Navigate to **Projects → [Your Project] → Harmonization**
2. Click on a syntactic mapping (e.g. "Patients → OMOP Person")
3. You can see the field-level transformation rules and inspect whether any source columns were missed
4. Click into a semantic mapping to see the term-level approvals and add any missing source values

### Reviewing the Harmonization Run
1. Navigate to **Projects → [Your Project] → Code Runs**
2. Find the harmonization code run (it will be labelled with the syntactic mapping name)
3. Click it to see the input dataset, output dataset, timing, and any warnings in the logs

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](support@rhinohealth.com)
