# Rhino SDK - Resource Utilization

## Description

Checks whether the workgroups collaborating on a Rhino FCP project currently have enough
free CPU, memory, storage, and GPU capacity to safely run a job, *before* you actually kick
that job off.

Rather than trusting a single instantaneous reading, each workgroup's resource usage is
sampled several times over a short window and reduced to worst-case ("peak") values - a
single snapshot could catch a workgroup at an unusually quiet moment and give a false sense
of security. Those peak values are then compared against thresholds you set (e.g. "CPU usage
must stay under 40%"), and any failing metric is reported with the exact value and by how
much it missed the threshold.

The notebook walks through four steps:
1. Log in to Rhino.
2. Load the target project and its collaborating workgroups.
3. Sample each workgroup's live resource usage and print a summary.
4. Re-sample (fresh data, right before you'd actually run your job) and check the peak usage against your thresholds - printing exactly what failed and by how much for any workgroup that doesn't meet them.

## Resources

- **[resource-utilization-notebook.ipynb](resource-utilization-notebook.ipynb)** - the walkthrough notebook. Logs in to Rhino, loads a project's collaborating workgroups, samples each workgroup's live resource usage over a short window, and checks the worst-case ("peak") usage against configurable thresholds to decide if it's safe to proceed. Handles edge cases such as no project/multiple projects matching a name, and a project with no collaborating workgroups.
- **[utils.py](utils.py)** - helper functions used by the notebook:

  - **`sample_agent_resources(project, workgroup_uid, num_samples=10, duration_sec=30)`**
    - queries a workgroup's agent resources repeatedly, spread evenly over
    `duration_sec` seconds, and returns the list of raw `SystemResources` samples.
    - `project` - Rhino SDK `Project` object.
    - `workgroup_uid` - UID of the workgroup to sample.
    - `num_samples` - number of samples to collect.
    - `duration_sec` - total time in seconds over which the samples are spread.
    - Raise both for a longer-running or more resource-intensive job, to get a better sense of sustained peak load rather than a brief blip. Lower them for a quick sanity check - just be aware fewer/closer-together samples are more likely to miss a real peak.

  - **`parse_system_resources(resources)`** - parses a single `SystemResources` object,
    or a list of them, into a plain dict of `cpu`/`memory`/`storage`/`gpu` metrics. Given
    a list, reduces it to the peak (worst-case) value per metric: max for usage
    percentages and used-GB, min for free-GB.
    - `resources` - a single `SystemResources` object, or a list of them, as returned by
      the Rhino SDK (e.g. by `sample_agent_resources`).

  - **`print_system_resources(parsed, wg_name)`** - prints a formatted summary of a
    parsed metrics dict for a given workgroup name.
    - `parsed` - parsed resource dict from `parse_system_resources`.
    - `wg_name` - workgroup display name to show in the summary header.

  - **`check_resource_thresholds(parsed, cpu_threshold=None, ram_free_gb_threshold=None, gpu_threshold=None, gpu_memory_threshold=None)`**
    - checks a parsed metrics dict against optional thresholds. Returns a dict, not a bool:
    `{"passed": bool, "failures": [...]}`. `failures` lists *every* threshold that was missed
    (not just the first one hit), each with the metric name, actual peak value, threshold, and
    a human-readable `detail` string explaining the failure and by how much (e.g. "CPU usage
    peaked at 62.3%, 22.3 percentage points over the 40.0% limit"). Any threshold left as
    `None` is skipped entirely for that metric, rather than treated as "no limit".
    - `parsed` - parsed resource dict from `parse_system_resources`.
    - `cpu_threshold` - max allowable CPU usage (%).
    - `ram_free_gb_threshold` - minimum required free RAM (GB).
    - `gpu_threshold` - max allowable GPU **compute** usage (%); at least one device must meet this.
    - `gpu_memory_threshold` - max allowable GPU **memory** usage (%); at least one device must meet this. This is a usage percentage, not a GB value - the platform doesn't expose absolute VRAM capacity per device, only percent-used.
    - **Edge case:** if `gpu_threshold` or `gpu_memory_threshold` is set to a *nonzero* value and a workgroup has no GPU at all, that workgroup automatically fails - there's no GPU device to evaluate against. Leave both as `None` if your job doesn't need a GPU.

## Prerequisites

- A Rhino FCP account with access to the project you want to check.
- The `rhino_health` Python SDK installed (`pip install rhino_health`).
- The target project must have at least one collaborating workgroup - there's nothing for this notebook to check otherwise (it raises a clear error if not).

## How to Run

1. Open `resource-utilization-notebook.ipynb`.
2. In step 1, set `USERNAME` to your Rhino FCP username; you'll be prompted for your password via a hidden `getpass` field when you run the cell.
3. In step 2, set `PROJECT` to the exact (case-sensitive) name of the project whose workgroups you want to check.
4. Run all cells top to bottom. Steps 3-4 each sample every collaborating workgroup for ~30 seconds by default, so expect the notebook to take a few minutes total for multiple workgroups.
5. In step 4, adjust the four threshold values (`cpu_threshold`, `ram_free_gb_threshold`, `gpu_threshold`, `gpu_memory_threshold`) to match what your job actually needs before relying on the PASS/FAIL result - see the per-parameter guidance in the notebook's step 4 cell for concrete guidance on when/why to change each one.

## Troubleshooting

- **A project you expect to find isn't found, or the wrong one loads** - step 2 handles both explicitly: no matching project raises a clear error, and multiple projects sharing the same name print a warning naming which one (the most recently created) was used - rename the project to something unique, or note its UID and load it explicitly if that's not the one you meant.
- **A workgroup with no GPU always fails when GPU thresholds are set** - this is expected: see the "Edge case" note under `check_resource_thresholds` above. Leave `gpu_threshold`/`gpu_memory_threshold` as `None` if your job doesn't require a GPU.

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
