# Tutorial 1 — Dataset Registration & Schema Generation

This is the first step of the data engineering workflow. Before we can analyze, clean, or harmonize data on the Rhino FCP, we need to tell the platform that the data exists and describe its structure. That is what this tutorial covers.

---

## What You Will Do

1. Log into the Rhino FCP from a Python notebook
2. Register all three source datasets (patients, encounters, procedures) with the platform
3. Automatically generate a Data Schema for each dataset — a description of each column's name and type
4. Review and, if needed, correct any type misclassifications
5. Link each schema back to its dataset

---

## Key Concepts

### What Is a Dataset?

In the Rhino FCP, a **Dataset** is a pointer to a data file (typically tabular data, like a CSV) that lives on a site's client node. It is **not** a copy of the data — it is a registration record that tells the platform:

- Which file to use (its path on the server)
- Which project it belongs to
- Which site (workgroup) owns it
- Basic statistics: row count, column names, file size

When you register a dataset, the Rhino client reads the file locally to collect these statistics and sends only that metadata to the FCP cloud. The patient data itself never moves.

Datasets in the FCP have a lifecycle:
- **Registered** — the agent has confirmed the file exists and gathered metadata
- **Schema attached** — a Data Schema has been linked, enabling validation and harmonization
- **Processing** — a Code Object is currently running against it (read-only during this time)

You can view all registered datasets for a project in the FCP Dashboard under **Projects → [Your Project] → Datasets**.

### What Is a Data Schema?

A **Data Schema** is a formal description of a dataset's structure. It records:

- The name of each column
- The **data type** of each column (what kind of values it holds)
- Optional metadata like a human-readable description or whether the field is required

Schemas are used in two critical ways in this workflow:

1. **Validation at runtime** — before a Code Object runs, the platform checks that the input dataset matches the expected schema. This catches errors early.
2. **Harmonization** — the OMOP mapping process in Tutorial 4 needs to know your source column types to generate correct transformation rules.

#### Supported Data Types

The Rhino FCP supports the following field data types:

| Type | Description | Example Values |
|------|-------------|----------------|
| `string` | Any text | `"Female"`, `"Outpatient"`, `"99213"` |
| `integer` | Whole number | `1001`, `1978`, `45378` |
| `float` | Decimal number | `98.6`, `72.4` |
| `date` | Calendar date | `2021-07-05` |
| `datetime` | Date and time | `2021-07-05 14:32:00` |
| `boolean` | True or false | `True`, `False` |

Choosing the right type matters. A date stored as `string` will not be recognized as a date by the harmonization engine. An integer ID stored as `float` can introduce decimal precision where none belongs.

#### Schema Versioning

Schemas are versioned in the FCP. If you update a schema after attaching it to a dataset, you create a new version rather than overwriting the original. This preserves an audit trail, which is important in regulated research environments.

### What Is Auto-generation?

Rather than requiring you to define every column type manually, the platform can look at a sample of your data and infer each column's type. This is called **schema auto-generation**.

Auto-generation works well for most cases but has known failure modes with our example data:

| Column | Expected Type | What Auto-generation Often Infers | Why |
|--------|--------------|----------------------------------|-----|
| `DateOfService` | `date` | `string` | Dates formatted as `YYYY-MM-DD` look like text strings |
| `ProcedureDate` | `date` | `string` | Same reason |
| `ProcedureCode` | `integer` | `integer` | Usually correct — verify it isn't inferred as `float` |
| `YearOfBirth` | `integer` | `integer` | Usually correct |

Step 4 of the notebook shows how to correct any misclassified fields.

---

## About the Example Datasets

### `encounters.csv` — 100 rows
One row per clinical visit. Maps to the OMOP `visit_occurrence` table in Tutorial 4.

| Column | Expected Type | Description |
|--------|--------------|-------------|
| `patientID` | integer | Foreign key linking to `patients.csv` |
| `visitID` | integer | Unique identifier for this visit |
| `DateOfService` | date | Date the visit took place (`YYYY-MM-DD`) |
| `TypeOfService` | string | Visit setting. Values: `Outpatient`, `Inpatient`, `Emergency` |

### `patients.csv` — 100 rows
One row per patient. Maps to the OMOP `person` table in Tutorial 4.

| Column | Expected Type | Description |
|--------|--------------|-------------|
| `patientID` | integer | Unique identifier for each patient. Primary key — must be non-null and unique. |
| `YearOfBirth` | integer | Year the patient was born (e.g. `1978`). Not a full date — just the year. |
| `Gender` | string | Values in this dataset: `Male`, `Female`, `Other` |
| `Race` | string | Values: `White`, `Black`, `Asian`, `Other` |
| `Ethnicity` | string | Values: `Hispanic`, `Non-Hispanic` |

### `procedures.csv` — 100 rows
One row per procedure performed during a visit. Maps to the OMOP `procedure_occurrence` table in Tutorial 4.

| Column | Expected Type | Description |
|--------|--------------|-------------|
| `patientID` | integer | Foreign key linking to `patients.csv` |
| `visitID` | integer | Foreign key linking to `encounters.csv` |
| `ProcedureDate` | date | Date the procedure was performed (`YYYY-MM-DD`) |
| `ProcedureDescription` | string | Free-text description of the procedure |
| `ProcedureCode` | integer | CPT (Current Procedural Terminology) code. Examples: `99213`, `45378` |
| `ProcedureCategory` | string | Values: `Patient Education`, `Surgical Procedure`, `Emergency Services` |

---

## Prerequisites

What You Need Before Starting:

1. **Tutorial 0 Complete** — 3 CSV files are present on the Rhino client (encounters, patients, procedures)
2. **Active FCP Credentials** - your username and password
3. **`PROJECT_UID`** — find in the FCP Dashboard: log in → from the Projects landing page, click on the 3 dots on the top right hand corner of your specified project, and "Copy UID"
- When you create your project, it is highly recommended that you set the k-anonymization parameter to 1, instead of leaving it as the default of 5 (this will faciliate viewing of extraneous values during tutorial 2)

---

## Running the Notebook

See `Running Notebooks` section in root level [README.md](../README.md)

Open `notebooks/dataset_registration.ipynb` and select the **rhino_data_engineering** kernel.

The notebook is structured with one section per dataset. **Each section is independent** — you can run only the sections you need, or skip a section if that dataset was already registered in a previous session. Always run the **Configuration** and **Authentication** cells first.

---

## Checking Your Work in the FCP Dashboard

After running each section of the notebook, you can verify the results visually via the FCP UI at [https://dashboard.rhinohealth.com/login](https://dashboard.rhinohealth.com/login).

### Verifying Dataset Registration
1. Navigate to **Projects → [Your Project]**
2. Click the **Datasets** tab
3. You should see your newly registered datasets listed with their names, row counts, and the workgroup they belong to
4. If `row_count` shows as `—` or `pending`, wait 1–2 minutes and refresh — the agent processes this asynchronously

### Verifying Schema Generation
1. Navigate to **Projects → [Your Project] → Data Schemas**
2. You should see three new schemas (one per dataset)
3. Click into a schema to inspect the field list and verify the data types look correct
4. If you corrected any types in the notebook, confirm the correction shows here. Alternatively, you can perform corrections directly in the UI.

> Remember that editing a schema creates a new version

### Verifying Schema Attachment
1. Navigate back to the **Datasets** tab
2. Click into a dataset
3. The **Schema** field should show the name of the attached schema (not blank)

---

## Outputs — Save These UIDs

The final cell of the notebook prints six UIDs. **Copy and save all six** before moving to Tutorial 2.

```
PATIENTS_DATASET_UID   = '...'
ENCOUNTERS_DATASET_UID = '...'
PROCEDURES_DATASET_UID = '...'
PATIENTS_SCHEMA_UID    = '...'
ENCOUNTERS_SCHEMA_UID  = '...'
PROCEDURES_SCHEMA_UID  = '...'
```

If you lose a UID, you can retrieve it via: 
- **FCP Dashboard** - click on the 3 dots on the right side of a dataset or schema and and select "Copy UID" 
- **Web URL** - click into a dataset or schema and inspect the end of the url
- **Rhino SDK** (e.g., `session.dataset.get_datasets(project_uid=PROJECT_UID)`)

---

## Common Questions

**Q: What if the CSV path is wrong and registration fails?**

You will see an error from the agent saying the file was not found. Confirm the exact path on the client server with your administrator. Remember: the path must be on the *server*, not locally on your laptop.

**Q: What if row_count shows as "pending" in the notebook output?**

This is normal — the agent processes some statistics asynchronously. Wait a minute and check the Dashboard.

**Q: I see a date column typed as "string". Do I have to fix it now?**

Yes, fix it before proceeding to Tutorial 4. Harmonization requires date columns to be typed as `date`. Step 4 of the notebook has commented-out correction code — uncomment the relevant lines and run the cell.

**Q: Can I register the same dataset twice by accident?**

Yes. If you run the registration cell twice, you will create two records (each with a unique dataset_uid) pointing to the same file. This won't cause errors, but it is messy. If it happens, delete the duplicate via the Dashboard: **Datasets tab → click the duplicate → Delete**.

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](support@rhinohealth.com)
