# Tutorial 3 — Data Preparation via Code Objects

This tutorial cleans and standardizes the three prepared datasets using **Python Code Objects** — automated scripts that execute directly on the site's server. After this step, your data will be in a consistent, well-structured format ready for OMOP harmonization in Tutorial 4.

---

## What You Will Do

1. Write three Python cleaning scripts (one per dataset), each defined directly in the notebook
2. Register each as a Code Object in the Rhino FCP
3. Run each Code Object against its source dataset
4. Receive three cleaned output datasets, still on-site, registered with the FCP

---

## Key Concepts

### What Is a Code Object?

A Code Object is a Python script or Docker container that you register with the Rhino FCP for execution on a site's on-premises server. Think of it as sending a sealed instruction packet to someone at the hospital: *"Take the patients file, apply these exact rules, and hand me back a cleaned version."* The person (the Rhino agent) opens the instructions locally and does the work — you never touch the original data.

When you run a Code Object, the platform:
1. Sends it to the client
2. Creates an **isolated container** on the server — a sandboxed environment with no external network access
3. Places the input dataset at the standard path `/input/0/dataset.csv`
4. Executes the script inside the container
5. Reads the output from `/output/0/dataset.csv`
6. Registers the output as a new dataset on the FCP (metadata only — the data stays on-site)

The container is discarded when the run completes.

See [link](https://docs.rhinohealth.com/hc/en-us/articles/12384939376669-What-is-a-Code-Object) for more info

### Supported Code Object Types

The Rhino FCP supports several types of Code Objects:

| Type | Use Case |
|---|---|
| **Python Code** | Custom Python scripts — this tutorial uses this type |
| **Generalized Compute (Docker)** | Any language or framework packaged as a Docker container |
| **Interactive Container** | A live browser-accessible session that accesses data on site (covered in Tutorial 2) |
| **NVFlare** | Federated model training using the NVIDIA FLARE framework |

For data preparation, Python Code Objects are the right choice. They are lightweight, fast to register, and support the standard `pandas`/`numpy` environment by default.

See [link](https://docs.rhinohealth.com/hc/en-us/articles/12385157324829-Supported-Code-Object-Types-on-the-Rhino-FCP) for more info

### What Is a Code Run?

A **Code Run** is an execution record for a Code Object. It tracks:
- Which Code Object was executed
- Which input datasets were used
- Which output datasets were produced
- The run's status (Queued, Running, Completed, Failed)
- Start and end times
- Execution logs

Code Runs are persisted in the FCP — you can always go back and see exactly what ran, when, on what data, and what it produced. This auditability is important in regulated research settings.

See [link](https://docs.rhinohealth.com/hc/en-us/articles/12385247215005-What-is-a-Code-Run) for more info

### Standard I/O File Paths

All Code Objects use the same file paths regardless of content:

| Path | Description |
|---|---|
| `/input/dataset.csv` | Single input dataset | 
| `/input/0/dataset.csv` | First input dataset (if multiple inputs)  |
| `/input/1/dataset.csv` | Second input dataset (if multiple inputs) |
| `/input/run_params.json` | Optional JSON runtime parameters |
| `/output/0/dataset.csv` | Where the script writes its output |

The container always has these paths available — you do not need to create them.

### Why Three Separate Code Objects?

Each of the three datasets requires different cleaning logic. Keeping them as three independent Code Objects means:
- You can re-run one dataset's prep without reprocessing the others
- If one run fails, you debug and re-run only that one
- Each Code Object is descriptively named and self-contained, making the project easier to audit and maintain
- Code Objects are reusable — once registered, run the same script against a new dataset at any site with a single call

---

## What Each Script Does

### Patients Preparation
| Transformation | Why It Is Needed |
|---|---|
| Standardize `Gender` to title case | Source data may contain `"male"`, `"MALE"`, and `"Male"` — all meaning the same thing. OMOP mapping requires consistent casing to match semantic mapping entries. |
| Validate `YearOfBirth` is between 1900–2025 | Catches data entry errors like `202` (missing a digit) or `19780101` (a full date accidentally in the year field) |
| Drop exact duplicate rows | Prevents patients from being counted multiple times in analytics |
| Drop rows missing `patientID` | A patient without an ID cannot be linked to encounters or procedures in the OMOP model |

### Encounters Preparation
| Transformation | Why It Is Needed |
|---|---|
| Parse `DateOfService` to `YYYY-MM-DD` | OMOP requires date fields in a standard parseable format |
| Standardize `TypeOfService` to title case | Consistent values (`"Outpatient"` not `"outpatient"`) are required for semantic mapping to OMOP visit concepts |
| Drop rows missing `patientID` or `visitID` | Records without both IDs cannot be linked in OMOP |
| Drop duplicate rows | Prevents visits from being counted multiple times |

### Procedures Preparation
| Transformation | Why It Is Needed |
|---|---|
| Parse `ProcedureDate` to `YYYY-MM-DD` | Required for OMOP `procedure_date` field |
| Drop rows where `ProcedureCode` is null | A procedure without a CPT code cannot be mapped to an OMOP concept — the harmonization step would produce a null `procedure_concept_id` for these rows |
| Drop rows missing `patientID` or `visitID` | Orphaned procedure records cannot be linked |
| Drop duplicate rows | Prevents procedures from being counted multiple times |

---

## What You Need Before Starting

1. Completed Tutorial 1 — six UIDs needed in the Configuration cell
2. Your login credentials
3. Your `PROJECT_UID`

---

## Running the Notebook

Open `notebooks/data_preparation.ipynb` and select the **rhino_data_engineering** kernel.

**Run the Configuration cell and the Shared Utilities cell first.** These must be executed before any dataset section, as they define the helper functions that all three sections use.

Each dataset section (1 of 3, 2 of 3, 3 of 3) is **fully independent**:
- Run all three in order, or
- Skip a section if that dataset is already prepared from a previous session, or
- Re-run a single section if a run failed

Each section has exactly two execution cells:
1. **Define the script** — sets the code as a Python string variable (does not run yet)
2. **Register and run** — registers the Code Object (or reuses an existing one) and executes it against the source dataset, polling until complete

A typical run takes 1–3 minutes. The polling output looks like:

```
Logged in as: Your Name
Code Object already exists — reusing: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Run initiated: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
  [  15s]  Running
  [  30s]  Running
  [  45s]  Completed

Run completed successfully.
```

---

## Checking Your Work in the FCP Dashboard

After running the notebook sections:

### Verifying Code Objects
1. Navigate to **Projects → [Your Project] → Code**
2. Three Code Objects should be present, 1 per dataset:
* `Data Prep — Patients`
* `Data Prep — Encounters`
* `Data Prep — Procedures`
3. These are saved and reusable — click any one to see its script, description, and run history

### Verifying Code Runs
1. Navigate to **Projects → [Your Project] → Code Runs**
2. All executed runs should appear (in theory, assuming you ran each code object 1 time for each of the 3 datasets, you'll see 3 corresponding runs)
3. Each run shows: the Code Object name, input dataset, output dataset, status, and duration
4. Click a run to expand it and see the execution logs — the `print()` statements from your script appear here

### Verifying Output Datasets
1. Navigate to **Projects → [Your Project] → Datasets**
2. Three new datasets should be present, 1 per dataset, with `— Prepared` in their names
3. Click any dataset to verify:
   - **Row count** should equal or be slightly less than the source dataset (if rows were dropped)
   - **Schema** should show an auto-inferred schema name (not blank)
   - Use the **Analytics** tab to verify distributions look reasonable

---

## Outputs — Copy These UIDs

The final cell prints six UIDs for the prepared datasets and their schemas. **Save all six before moving to Tutorial 4.**

```
PREPARED_PATIENTS_UID          = '...'
PREPARED_ENCOUNTERS_UID        = '...'
PREPARED_PROCEDURES_UID        = '...'
PREPARED_PATIENTS_SCHEMA_UID   = '...'
PREPARED_ENCOUNTERS_SCHEMA_UID = '...'
PREPARED_PROCEDURES_SCHEMA_UID = '...'
```

---

## Common Questions

**Q: The run failed. Where do I see what went wrong?**
The notebook automatically fetches and prints the logs when a failure is detected. Look for the `Run did not complete. Logs:` section in the output. The Python error message from inside the script will appear there. You can also view the logs in the Dashboard under **Code Runs → click the failed run → Logs tab**.

**Q: "Code Object already exists — reusing" appears. Is that okay?**
Yes, this is intentional. The `register_or_reuse_code_object` helper checks for an existing Code Object with the same name. Reusing it avoids clutter. If you need to update the script logic, change the `name=` argument to create a new version.

**Q: The output row count is lower than the input. Is that a problem?**
Depends. For the example data, all 100 rows should pass through cleanly. If rows were dropped, check the run logs — the script prints a message for every row-dropping operation, showing exactly how many rows were removed and why.

**Q: Can I test the cleaning script locally before registering it?**
Yes. Copy the script string contents to a `.py` file, replace `/input/0/dataset.csv` with a local CSV path, and run it with `python your_script.py`. This is the fastest way to validate logic before deploying to the site. Alternatively, use an Interactive Container (Tutorial 2) to run exploratory code directly on the server data.

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](support@rhinohealth.com)
