# Federated EAP Analytics — Rhino FCP Metric Reference

This document describes every federated metric used across the three analysis modules.
Each metric is computed locally at each participating site and aggregated centrally by
Rhino — no raw employee records are transferred at any point.

More general documentation on the Rhino federated metrics suite can be found within our [Calculating Federated Analytics](https://docs.rhinofcp.com/rhino-sdk/calculating-federated-analytics-part-1#retrieving-a-metric) documentation and our [Metrics API](https://rhinohealth.github.io/rhino_sdk_docs/html/autoapi/rhino_health/lib/metrics/index.html) documentation.

---

## How Federated Metrics Work

All metrics share a common execution pattern:

```python
config = MetricClass(variable="column_name", **options)
result = session.project.aggregate_dataset_metric(dataset_uids, config)
output = result.output
```

`dataset_uids` is a list of one or more dataset UIDs. Passing multiple UIDs triggers
federated aggregation — each site computes the metric locally and Rhino combines the
results centrally using mathematically equivalent pooling (e.g. weighted means,
pooled variances, combined sufficient statistics).

```python
# Single site
result = session.project.aggregate_dataset_metric([hq_uid], config)

# Federated across both sites
result = session.project.aggregate_dataset_metric([hq_uid, customer_uid], config)
```

---

## Shared Options

Two optional parameters are available on most metrics and can be combined freely.

### `group_by`

Splits the metric by one or more categorical columns, returning a result per group.

```python
Mean(
    variable="business_days_absent_per_year",
    group_by={"groupings": ["used_mental_health_benefit"]}
)
```

Output structure:
```python
{
    "True":  {"mean": 1.93, ...},
    "False": {"mean": 2.94, ...}
}
```

### `data_filters`

Restricts the metric to a subset of rows matching one or more conditions.
Multiple filters are combined with AND logic.

```python
Mean(
    variable="total_annual_healthcare_costs_usd",
    group_by={"groupings": ["job_level"]},
    data_filters=[
        {"filter_column": "age", "filter_type": ">=", "filter_value": 41},
        {"filter_column": "age", "filter_type": "<=", "filter_value": 50},
    ]
)
```

Supported `filter_type` values:

| Operator | Description |
|---|---|
| `=` | Exact match |
| `>=` | Greater than or equal |
| `<=` | Less than or equal |
| `>` | Greater than |
| `<` | Less than |

`group_by` and `data_filters` can be used together:

```python
# Mean absence per job level, restricted to employees aged 41-50
Mean(
    variable="business_days_absent_per_year",
    group_by={"groupings": ["job_level"]},
    data_filters=[
        {"filter_column": "age", "filter_type": ">=", "filter_value": 41},
        {"filter_column": "age", "filter_type": "<=", "filter_value": 50},
    ]
)
```

---

## Metrics

### `Count`

```python
from rhino_health.lib.metrics import Count
```

Counts the number of non-null values in a column. When used with `group_by`, returns
a count per group — useful for computing proportions from categorical columns.

**Basic usage:**
```python
count_config = Count(variable="employee_id")
result = session.project.aggregate_dataset_metric(dataset, count_config).output
# {"count": 43827}
```

**With `group_by` (categorical proportions):**
```python
count_config = Count(
    variable="used_mental_health_benefit",
    group_by={"groupings": ["used_mental_health_benefit"]}
)
result = session.project.aggregate_dataset_metric(dataset, count_config).output
# {"True": {"count": 18337}, "False": {"count": 25490}}

utilization_pct = result["True"]["count"] / (result["True"]["count"] + result["False"]["count"])
```

**With `data_filters` (department-level counts):**
```python
count_config = Count(
    variable="employee_satisfaction",
    group_by={"groupings": ["employee_satisfaction"]},
    data_filters=[
        {"filter_column": "department", "filter_type": "=", "filter_value": "Engineering"}
    ]
)
```

**Used in:** Module 1 (EAP utilisation, satisfaction distribution, funnel),
Module 2 (department hotspot map)

---

### `Mean`

```python
from rhino_health.lib.metrics import Mean
```

Computes the arithmetic mean of a numeric column. In the federated setting, Rhino
pools sufficient statistics (sum and count) from each site to produce a result
equivalent to computing the mean on the full combined dataset.

**Basic usage:**
```python
mean_config = Mean(variable="business_days_absent_per_year")
result = session.project.aggregate_dataset_metric(dataset, mean_config).output
# {"mean": 2.76}
```

**With `group_by`:**
```python
mean_config = Mean(
    variable="business_days_absent_per_year",
    group_by={"groupings": ["used_mental_health_benefit"]}
)
result = session.project.aggregate_dataset_metric(dataset, mean_config).output
# {"True": {"mean": 1.93}, "False": {"mean": 2.94}}
```

**With `data_filters`:**
```python
mean_config = Mean(
    variable="satisfaction_score",
    data_filters=[
        {"filter_column": "eap_total_services_used", "filter_type": "=", "filter_value": 3}
    ]
)
result = session.project.aggregate_dataset_metric(dataset, mean_config).output
# {"mean": 3.43}
```

**Used in:** Module 1 (healthcare cost heatmap), Module 2 (satisfaction vs services,
absenteeism by MH benefit, department hotspot map), Module 3 (healthcare cost heatmap)

---

### `StandardDeviation`

```python
from rhino_health.lib.metrics import StandardDeviation
```

Computes the standard deviation of a numeric column. Also returns the mean and
variable count, making it useful for deriving standard error and sample size
in a single query. Federated pooling uses the parallel variance formula to combine
site-level variances without transferring raw data.

**Basic usage:**
```python
std_config = StandardDeviation(variable="business_days_absent_per_year")
result = session.project.aggregate_dataset_metric(dataset, std_config).output
# {"stddev": 2.42, "mean": 2.76, "variable_count": 72981}
```

**With `group_by`:**
```python
std_config = StandardDeviation(
    variable="business_days_absent_per_year",
    group_by={"groupings": ["used_mental_health_benefit"]}
)
result = session.project.aggregate_dataset_metric(dataset, std_config).output
# {
#   "True":  {"stddev": 2.18, "mean": 1.93, "variable_count": 18337},
#   "False": {"stddev": 2.32, "mean": 2.94, "variable_count": 25490}
# }
```

The `variable_count` field is particularly useful — it gives you the per-group
sample size without needing a separate `Count` query.

**Used in:** Module 2 (absenteeism bar chart, Cohen's d), Module 3 (ROI regression slope)

---

### `Percentile`

```python
from rhino_health.lib.metrics import Percentile
```

Computes a single percentile value for a numeric column. Because computing exact
federated quantiles requires transferring rank information, Rhino uses an approximate
algorithm that is both privacy-preserving and computationally efficient.

One query is required per percentile value. For distribution reconstruction, querying
`[10, 25, 50, 75, 90]` gives a good balance of shape fidelity and query volume.

**Basic usage:**
```python
pct_config = Percentile(
    variable="business_days_absent_per_year",
    percentile=50  # median
)
result = session.project.aggregate_dataset_metric(dataset, pct_config).output
# {"business_days_absent_per_year": 2.0}
```

**Querying multiple percentiles:**
```python
PERCENTILES = [10, 25, 50, 75, 90]

percentiles = {}
for p in PERCENTILES:
    result = session.project.aggregate_dataset_metric(
        dataset,
        Percentile(variable="business_days_absent_per_year", percentile=p)
    ).output
    percentiles[p] = result["business_days_absent_per_year"]

# {10: 0.0, 25: 1.0, 50: 2.0, 75: 4.0, 90: 5.0}
```

**Note:** `data_filters` and `group_by` are supported but each combination requires
a separate query. For heavily filtered percentile grids, query volume can grow quickly.

**Used in:** Module 2 (absence distribution violin plot)

---

### `TTest` (Welch's Two-Sample T-Test)

```python
from rhino_health.lib.metrics.statistics_tests import TTest
```

Performs a Welch's t-test comparing the mean of a numeric variable across two groups
defined by a binary categorical variable. Welch's formulation is used (rather than
Student's) because it does not assume equal variance between groups.

Returns the t-statistic, p-value, and degrees of freedom. The non-integer degrees of
freedom confirm the Welch adjustment is applied.

**Basic usage:**
```python
t_test_config = TTest(
    numeric_variable="business_days_absent_per_year",
    categorical_variable="used_mental_health_benefit"
)
result = session.project.aggregate_dataset_metric(dataset, t_test_config).output
# {
#   "t_test": {
#     "statistic": -46.78,
#     "p_value": 0.0,
#     "dof": 40934.03
#   }
# }
```

**Interpreting results:**
- `statistic` — magnitude indicates how many standard errors separate the group means;
  sign reflects group ordering
- `p_value` — probability of observing this difference by chance under the null hypothesis;
  values below 0.05 are conventionally significant
- `dof` — degrees of freedom; non-integer values confirm Welch's adjustment for unequal
  variances and sample sizes

**Note:** `TTest` takes `numeric_variable` and `categorical_variable` rather than the
standard `variable` parameter. `group_by` and `data_filters` are not supported.

**Used in:** Module 2 (absenteeism users vs non-users significance test)

---

### `Pearson`

```python
from rhino_health.lib.metrics.statistics_tests import Pearson
```

Computes the Pearson correlation coefficient between two numeric variables. Federated
computation uses covariance sufficient statistics (sum of cross-products, individual
sums, and counts) pooled across sites — mathematically equivalent to computing
the correlation on the full combined dataset.

Returns a value between -1 (perfect negative linear relationship) and +1 (perfect
positive linear relationship), with 0 indicating no linear relationship.

**Basic usage:**
```python
pearson_config = Pearson(
    variable_1="business_days_absent_per_year",
    variable_2="used_mental_health_benefit"
)
result = session.project.aggregate_dataset_metric(dataset, pearson_config).output
# {"correlation": -0.18}
```

**Computing a correlation matrix:**
```python
from itertools import product

outcome_vars = ["business_days_absent_per_year", "satisfaction_score", ...]
service_vars = ["used_mental_health_benefit", "used_wellness_program", ...]

correlations = {}
for v1, v2 in product(outcome_vars, service_vars):
    result = session.project.aggregate_dataset_metric(
        dataset,
        Pearson(variable_1=v1, variable_2=v2)
    ).output
    correlations[(v1, v2)] = result["correlation"]
```

**Note:** Boolean columns (`True`/`False`) are treated as `1`/`0` and are valid inputs.
Spearman correlation is available via `from rhino_health.lib.metrics.statistics_tests import Spearman`
but is significantly slower in the federated setting (~2 min per pair vs ~9 sec for Pearson)
due to the cost of rank computation across distributed data.

**Used in:** Module 3 (EAP service vs outcome correlation matrix, ROI regression slope)

---

## Metric Capability Matrix

| Metric | `group_by` | `data_filters` | Federated |
|---|:---:|:---:|:---:|
| `Count` | ✅ | ✅ | ✅ |
| `Mean` | ✅ | ✅ | ✅ |
| `StandardDeviation` | ✅ | ✅ | ✅ |
| `Percentile` | ✅ | ✅ | ✅ |
| `TTest` | ❌ | ❌ | ✅ |
| `Pearson` | ❌ | ❌ | ✅ |

---

## Additional Metrics Available in Rhino

The following metrics are available in the Rhino platform but were not used in this
analysis. They follow the same `aggregate_dataset_metric` pattern described above.

*Note: This does not encompass every available federated metric Rhino offers.*

| Metric | Import | Description |
|---|---|---|
| `Spearman` | `statistics_tests` | Rank-based correlation; more robust to outliers than Pearson but significantly slower federally |
| `OneWayANOVA` | `statistics_tests` | Tests whether means differ significantly across 3+ groups |
| `Median` | `metrics` | Federated approximate median |
| `Min` / `Max` | `metrics` | Federated minimum and maximum values |
| `Sum` | `metrics` | Federated sum of a numeric column |

