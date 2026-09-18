# Tutorial 4 — Harmonization with the Rhino Data Harmonization Engine (RhinoDHE)

This tutorial maps the three prepared datasets to **OMOP CDM** target tables using the Rhino Data Harmonization Engine. The result is a set of harmonized datasets conforming to a shared standard, enabling federated analytics and model training across sites without custom per-site translation code.

---

## Prerequisites

- Tutorial 3 complete — all 3 prepared datasets and their corresponding 3 schema UIDs are required
- OMOP target schemas pre-defined in the FCP (your Rhino administrator can create these, or use the Dashboard: Projects → Data Schemas → New Schema)
- Your `PROJECT_UID`

**Inputs:** Three prepared datasets from Tutorial 3

**Outputs:** Three OMOP-conformant datasets (OMOP Person, Visit Occurrence, Procedure Occurrence), registered on the Rhino client

---

## What You Will Do

1. Create Semantic Mappings (value-level vocabulary translations)
2. Review and approve AI-proposed term matches
3. Auto-generate Syntactic Mapping field rules
4. Run harmonization to produce OMOP-compliant output datasets

---

## About the Rhino Data Harmonization Engine (RhinoDHE)

The RhinoDHE is the Rhino FCP's system for transforming source data into a target data model in a structured, auditable, and reusable way. It is not limited to a single standard — it supports three target model types:

| Target Model | When to Use |
|---|---|
| **OMOP CDM** | Observational research, drug effectiveness studies, EHR data pooling. This tutorial uses OMOP. |
| **FHIR** | Interoperability with clinical systems, HL7/FHIR-based pipelines, real-time data exchange workflows. Built-in support in the Rhino DHE. |
| **Custom** | Any non-standard target schema you define. Used when the project requires a proprietary or institution-specific data model. Source vocabularies can be standard or custom. |

In all three cases, the harmonization mechanism is the same: a Semantic Mapping for value translation, and a Syntactic Mapping for structural transformation.

For more info, see [docs](https://docs.rhinohealth.com/hc/en-us/articles/20060155424413-About-the-Rhino-Data-Harmonization-Engine-RhinoDHE)


---

## Two Layers of Mapping

Harmonization operates at two distinct layers:

### Layer 1: Semantic Mapping (Value Translation)

Translates individual **values** between vocabularies:

| Source Value | Target Concept ID | Target Name |
|---|---|---|
| `"Male"` | 8507 | Male |
| `"Outpatient"` | 9202 | Outpatient Visit |
| `45378` (CPT) | 4287782 | Colonoscopy |

The platform proposes matches using AI. A data steward reviews and approves/rejects each pairing before the mapping can be used in a run. [docs](https://docs.rhinohealth.com/hc/en-us/articles/19820382979869-Creating-a-Semantic-Mapping)


**Status lifecycle:** `Not Started → In Progress → Needs Review → Approved`

### Layer 2: Syntactic Mapping (Structural Transformation)

Defines **field-level rules**: which source column maps to which target column, what type conversion to apply, and which semantic mapping to invoke for coded columns. [docs](https://docs.rhinohealth.com/hc/en-us/articles/23459070770461-Creating-a-Syntactic-Mapping)

### Syntactic Mapping Transformations

The auto-generated field rules in a Syntactic Mapping support a range of additional transformation types beyond simple column renaming:

| Transformation | Description | Example |
|---|---|---|
| **Direct copy** | Source value copied as-is to target | `patientID` → `person_id` |
| **Type cast** | Convert data type | integer → string |
| **Date format** | Parse and reformat a date | `"2021-07-05"` → OMOP date format |
| **Vocabulary lookup** | Replace source value with mapped concept ID | `"Male"` → `8507` |
| **Constant** | Always write a fixed value to the target column | `visit_type_concept_id = 32817` |
| **Expression** | Compute a derived value | `year_of_birth = YEAR(date_of_birth)` |
| **Split/combine** | Split one column into many or merge several | First/last name merge |

When auto-generation does not produce the right rule for a column, you can edit the syntactic mapping configuration manually via the SDK or the FCP Dashboard.


---

## Semantic Mapping (OMOP Concepts)

### Gender → OMOP Gender Concepts
| Source Value (after cleaning) | OMOP Concept ID | OMOP Name |
|---|---|---|
| Male | 8507 | Male |
| Female | 8532 | Female |
| Other | 8521 | Other |

### Race → OMOP Race Concepts
| Source Value | OMOP Concept ID | OMOP Name |
|---|---|---|
| Asian | 8515 | Asian |
| Black | 8516 | Black or African American |
| White | 8527 | White |
| Other | 8522 | Other Race |

### Ethnicity → OMOP Ethnicity Concepts
| Source Value | OMOP Concept ID | OMOP Name |
|---|---|---|
| Hispanic | 38003563 | Hispanic or Latino |
| Non-Hispanic | 38003564 | Not Hispanic or Latino |

### TypeOfService → OMOP Visit Concepts
| Source Value | OMOP Concept ID | OMOP Name |
|---|---|---|
| Outpatient | 9202 | Outpatient Visit |
| Inpatient | 9201 | Inpatient Visit |
| Emergency | 9203 | Emergency Room Visit |

### TypeOfService → Custom Encounter Type Concepts
| Source Value | Concept ID | Name                       |
|---|---|----------------------------|
| Outpatient | 2 | Outpatient Care            |
| Inpatient | 1 | Inpatient Care             |
| Emergency | 3 | Emergency Department Care  |

### ProcedureDescription → OMOP Procedure Concepts
| Source Value | OMOP Concept ID | Description |
|--------------|---|---|
| 45378        | 4287782 | Colonoscopy |
| 44950        | 4196867 | Appendectomy |
| 99203        | 4098498 | Office visit, new patient |
| 99212        | 4098460 | Office visit, established |
| 99213        | 4098462 | Office visit, established |
| 99285        | 4129922 | Emergency department visit |

---

## Syntactic Mapping (Source → OMOP Table)

| Source Dataset | OMOP Target Table | Key Column Mappings                                                                                                                                                                                                                                                 |
|---|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| patients (prepared) | `person` | `patientID`→`person_id`; `Gender`→`gender_concept_id`; `YearOfBirth`→`year_of_birth`; `Race`→`race_concept_id`; `Ethnicity`→`ethnicity_concept_id`;                                                                                                                 |
| encounters (prepared) | `visit_occurrence` | `visitID`→`visit_occurrence_id`; `patientID`→`person_id`; `TypeOfService`→`visit_concept_id`; `DateOfService`→`visit_start_date`; `DateOfService`→`visit_end_date`; `TypeOfService`→`visit_type_concept_id`;  `TypeOfService`→`visit_source_concept_id`             |
| procedures (prepared) | `procedure_occurrence` | `visitID`→`procedure_occurrence_id`; `patientID`→`person_id`; `ProcedureDescription`→`procedure_concept_id`; `ProcedureDate`→`procedure_date`; `ProcedureCategory`→`procedure_type_concept_id`; `visitID`→`procedure_occurrence_id` |

---

## Checking Your Work in the FCP Dashboard

### After Setup
1. Dashboard → Projects → [Your Project] → **Data Mappings** tab
2. The Data Mappings tab has three sub-tabs: **Syntactic Mappings**, **Semantic Mappings**, and **Custom Vocabularies**
3. Under **Syntactic Mappings** — you should see one Syntactic Mapping covering all three datasets (Person, Visit Occurrence, Procedure Occurrence)
4. Click into the Syntactic Mapping — some field transformations reference Semantic Mappings that require approval
5. Navigate to the **Semantic Mappings** sub-tab — the status of each Semantic Mapping should be **Needs Review** (ready for approval)

### After Approval
1. Semantic mapping status changes to **Approved**
2. Dashboard → Data Mappings → click the Syntactic Mapping → view the auto-generated field transformations

### After Running
1. Dashboard → **Code Runs** — the harmonization run appear
2. Click the run → Logs tab → verify no warnings about unmapped values
3. Dashboard → **Datasets** — three new OMOP output datasets appear
4. Click any OMOP dataset → **Analytics** tab → inspect concept ID distributions

---

## Common Pitfalls

- **"Semantic mapping cannot be used — status is Needs Review":** All terms must be approved before running. Review in Dashboard → Data Mappings → Semantic Mappings → click the mapping → approve/reject each entry.
- **High concept_id = 0 rate in output:** A source value was not included in your semantic mapping. Add it, re-approve, re-run.
- **"Auto-generate produced no field rules":** Source schema column names don't match what the mapping expects. Verify prepared dataset schema field names match exactly.

---

## Helpful Links

| Resource | Description |
|---|---|
| [About RhinoDHE](https://docs.rhinohealth.com/hc/en-us/articles/20060155424413) | Overview of the Rhino Data Harmonization Engine |
| [Creating a Syntactic Mapping](https://docs.rhinohealth.com/hc/en-us/articles/23459070770461) | Step-by-step guide for syntactic mapping setup |
| [Syntactic Mapping Transformations](https://docs.rhinohealth.com/hc/en-us/articles/22869986524061) | Full list of supported transformation types |
| [Creating a Semantic Mapping](https://docs.rhinohealth.com/hc/en-us/articles/19820382979869) | Guide for vocabulary-level term mapping |
| [Creating a Custom Vocabulary](https://docs.rhinohealth.com/hc/en-us/articles/19823208544413) | How to define your own vocabulary for non-standard source codes |
| [Running a RhinoDHE Code Object](https://docs.rhinohealth.com/hc/en-us/articles/23456568259485) | Guide for executing a harmonization run |
| [OMOP ETL via RhinoDHE](https://docs.rhinohealth.com/hc/en-us/articles/26126228977437) | OMOP-specific harmonization tutorial |
| [FHIR ETL via RhinoDHE](https://docs.rhinohealth.com/hc/en-us/articles/26128716368797) | FHIR-specific harmonization tutorial |
| [Rhino FCP Dashboard](https://dashboard.rhinohealth.com/login) | Web UI for monitoring runs and managing mappings |
| [Rhino SDK Docs](https://rhinohealth.github.io/rhino_sdk_docs/html/index.html) | Full SDK reference |
| [support@rhinohealth.com](mailto:support@rhinohealth.com) | Direct support |

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com)
