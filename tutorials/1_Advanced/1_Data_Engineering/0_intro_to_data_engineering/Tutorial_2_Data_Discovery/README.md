# Tutorial 2 — Data Discovery via Federated Analytics

This tutorial explores all three registered datasets using federated analytics — statistical queries that run on the site's server and return only aggregate results. You will learn what your data looks like before writing a single line of cleaning code.

---

## What You Will Do

1. Compute row counts and null rates across all three datasets
2. Explore Patients Dataset - profile demographics (gender, race, ethnicity distributions)
3. Explore Encounters Dataset - analyze encounter types & temporal coverage
4. Explore Procedure Dataset - evaluate codes and categories
5. Run federated SQL aggregate queries
6. Learn about **Interactive Containers** for deeper exploratory analysis

---

## Key Concepts

### What Is Federated Analytics?

Federated analytics means running statistical computations on data that stays on-site, and receiving only the aggregated results. This is the same principle that makes federated learning possible, applied to data exploration.

When you call `dataset.get_metric(Mean("age"))`, here is what happens:

1. Your notebook sends an instruction to the FCP cloud: *"Compute the mean of the 'age' column on dataset X"*
2. The FCP forwards this to the Rhino agent at the site hosting that dataset
3. The agent reads the CSV locally, computes the mean, and sends back a single number
4. You receive that number — not any individual patient rows

This means **you can ask meaningful questions about your data without anyone gaining access to the underlying records**. In a multi-site project, the FCP aggregates results from all sites automatically, giving you a combined answer.

#### What Kinds of Metrics Are Available?

The Rhino SDK's `rhino_health.lib.metrics` library includes (but is not limited to):

| Metric Class | What It Computes |
|---|---|
| `Count("col")` | Total count |
| `Mean("col")` | Arithmetic mean of a numeric column |
| `StandardDeviation("col")` | Standard deviation of a numeric column |
| `Sum("col")` | Sum of a numeric column |
| `Min("col")` / `Max("col")` | Minimum / maximum value |
| `Median("col")` | Median value |
| `Percentile("col", p)` | The p-th percentile |
| `Cox(...)` | Cox proportional hazard metric |
| `KaplanMeier(...)` | Kaplan-Meier survival analysis |

For complex queries beyond single-column metrics, federated SQL is available (see the SQL section in the notebook).

#### Privacy Suppression

The platform includes a privacy engine that may suppress individual histogram bins where a value appears in very few rows — this is intentional and prevents re-identification. If a histogram returns fewer bins than you expect, it does not mean the data is wrong; it means some rare values were withheld for privacy.

### What Is the Dataset Analytics View?

In addition to running metrics programmatically, the FCP Dashboard provides a built-in **Dataset Analytics** view for each registered dataset. To access it:

1. Navigate to **Projects → [Your Project] → Datasets**
2. Click on a dataset name
3. Click the **Analytics** tab

This view provides an automatic profile of every column: data type, count, null rate, and a histogram for categorical columns or a distribution chart for numeric columns. It is a good quick-check to run immediately after registering a dataset, before writing any code.

### What Is a Federated Dataset?

A **Federated Dataset** is a grouping of individual site datasets that share the same schema. Instead of running a metric on Site A's data and then Site B's data separately, you create a Federated Dataset that covers both, and run the metric once. The FCP routes the computation to each site and returns a single aggregated result.

This is the mechanism that makes multi-site research possible without sharing data. In this single-site tutorial, we demonstrate how to create one — even with one site, the pattern is identical to the multi-site case.

### What Is an Interactive Container?

An **Interactive Container** is a special type of Code Object that does not run a script and exit — instead, it starts a live, browser-accessible environment (e.g., a JupyterLab server) running directly on the site's server, with the dataset mounted at `/input/dataset.csv` for a single input, or `/input/<input_number>/dataset.csv` for multiple inputs (index starting at 0).

This is fundamentally different from the Code Objects used in Tutorial 3:

| | Standard Code Object | Interactive Container |
|---|---|---|
| **Mode** | Runs a script and exits | Starts a live environment |
| **Access** | Script output only | Full interactive session |
| **Use case** | Automated transformation | Exploratory analysis, debugging |
| **Duration** | Minutes | Hours (session-based) |
| **Data access** | Script reads input CSV | You browse files directly |

#### When to Use an Interactive Container

Interactive containers are most useful when:
- You want to explore the raw data interactively before deciding what transformations are needed
- A Code Object run is failing and you want to debug it by inspecting the data directly
- You need to write and test a new cleaning script before registering it as a formal Code Object
- A data steward at the site needs to manually inspect specific records to resolve a data quality issue

#### How to Launch an Interactive Container

Interactive containers are launched from the FCP Dashboard (not the SDK notebook):

1. Navigate to **Projects → [Your Project] → Code**
2. Click **Create New Code Object**
3. Select **Interactive Container** as the code object type
4. Provide a **Name** for the code object
5. Select input / output schemas (if you want to enforce structure)
6. Choose a base image (e.g. interactive-jupyter-notebook)
7. Click **Create New Code Object**
8. Click **Run** - and select input datasets
9. Once the container is running under **Code Runs** (status: `Active`), click the window link to launch the interface in your browser

Inside the container, your dataset is available at `/input/0/dataset.csv`. You can run arbitrary Python code, install packages, and save analysis results — but note that anything you want to keep must be written to `/output/0/` before the session ends, as the container environment is ephemeral.

> **Privacy note:** While Interactive Containers give you direct access to the dataset file, this access is governed by your FCP permissions. They are intended for authorized data stewards at the site, not for sharing data externally.

---

## What This Step Informs

Data discovery drives the decisions in every subsequent tutorial:

| Finding | Action |
|---|---|
| Date columns returned as strings in histograms | Fix schema type in Tutorial 1 (go back) |
| `Gender` values include `"male"`, `"MALE"`, `"Male"` | Plan case normalization in Tutorial 3 |
| `TypeOfService` has inconsistent casing | Plan normalization in Tutorial 3 |
| High null rate on a key column | Plan imputation or exclusion in Tutorial 3 |
| Unexpected CPT codes not in the reference list | Flag for manual review before Tutorial 4 mapping |
| Very low procedure counts for a code | May be privacy-suppressed — note for mapping coverage |

---

## Running the Notebook

See `Running Notebooks` section in root level [README.md](../README.md)

Open `notebooks/data_discovery.ipynb` and select the **rhino_data_engineering** kernel.

---

## Checking Your Work in the FCP Dashboard

### Viewing Dataset Analytics
1. Navigate to **Projects → [Your Project] → Datasets**
2. Click any dataset name
3. Select the **Analytics** tab
4. You will see an automatic column profile with null rates and value distributions — compare with your notebook output to confirm they match

### Monitoring Interactive Container Sessions
1. Navigate to **Projects → [Your Project] → Code Runs**
2. Active interactive container sessions appear here with status `Active`
3. Click **Open** to re-enter a running session
4. Click **Stop** when you are done — sessions that are left running consume compute resources

---

## Getting Help

For additional support, please reach out to [support@rhinofcp.com](support@rhinofcp.com)
