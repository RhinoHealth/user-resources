"""Helpers for sampling and evaluating a Rhino workgroup's system resources.
Used in conjunction with resource-utilization-notebook.ipynb."""

import time


def sample_agent_resources(project, workgroup_uid, num_samples=10, duration_sec=30):
    """
    Queries a workgroup's agent resources multiple times, spread evenly over a duration.

    Args:
        project (rhino_health.lib.endpoints.project.project_dataclass.Project): Rhino SDK Project object.
        workgroup_uid (str): UID of the workgroup to sample.
        num_samples (int): Number of samples to collect.
        duration_sec (float): Total time in seconds over which to spread the samples.

    Returns:
        list: SystemResources objects, one per sample.
    """
    interval = duration_sec / (num_samples - 1) if num_samples > 1 else 0
    samples = []
    for i in range(num_samples):
        samples.append(
            project.get_agent_resources_for_workgroup(project_uid=project.uid, workgroup_uid=workgroup_uid)
        )
        if i < num_samples - 1:
            time.sleep(interval)
    return samples


def parse_system_resources(resources):
    """
    Parses a Rhino SDK SystemResources object, or a list of them, into a
    human-readable dictionary.

    When given a list of samples, returns the peak (worst-case) value observed
    for each metric across the samples: the maximum for usage metrics
    (CPU/memory/storage/GPU used) and the minimum for free-space metrics
    (memory/storage free).

    Args:
        resources (SystemResources | list[SystemResources]): A single SystemResources
            object, or a list of them, as returned by the Rhino SDK.

    Returns:
        dict: Parsed and formatted resource metrics.
    """
    if isinstance(resources, (list, tuple)):
        parsed_samples = [_parse_single_system_resources(r) for r in resources]
        return _peak_parsed_resources(parsed_samples)
    return _parse_single_system_resources(resources)


def _parse_single_system_resources(resources):
    """
    Parses a single SystemResources object into a formatted dictionary.

    Args:
        resources (SystemResources): SystemResources object returned by the Rhino SDK.

    Returns:
        dict: Parsed and formatted resource metrics.
    """

    # Storage (convert bytes to GB)
    storage = resources.filesystem_storage
    storage_total_gb = storage['total'] / (1024 ** 3)
    storage_used_gb = storage['used'] / (1024 ** 3)
    storage_free_gb = storage['free'] / (1024 ** 3)
    storage_used_pct = (storage['used'] / storage['total']) * 100

    # Memory (convert bytes to GB)
    memory = resources.memory
    mem_total_gb = memory['total'] / (1024 ** 3)
    mem_used_gb = memory['used'] / (1024 ** 3)
    mem_free_gb = mem_total_gb - mem_used_gb
    mem_used_pct = (memory['used'] / memory['total']) * 100

    # CPU
    cpu_used_pct = resources.cpu_percent_used

    # GPU (handle cases where no GPU is available)
    gpu = resources.gpu
    gpu_compute = gpu.get('gpu_percent_used')
    gpu_memory = gpu.get('gpu_mem_percent_used')
    has_gpu = gpu_compute is not None and gpu_memory is not None

    parsed = {
        "cpu": {
            "used_pct": round(cpu_used_pct, 2)
        },
        "memory": {
            "total_gb": round(mem_total_gb, 2),
            "used_gb": round(mem_used_gb, 2),
            "free_gb": round(mem_free_gb, 2),
            "used_pct": round(mem_used_pct, 2)
        },
        "storage": {
            "total_gb": round(storage_total_gb, 2),
            "used_gb": round(storage_used_gb, 2),
            "free_gb": round(storage_free_gb, 2),
            "used_pct": round(storage_used_pct, 2)
        },
        "gpu": {
            device: {
                "compute_used_pct": round(gpu_compute.get(device, 0), 2),
                "memory_used_pct": round(gpu_memory.get(device, 0), 2)
            }
            for device in gpu_compute
        } if has_gpu else {}
    }

    return parsed


def _peak_parsed_resources(parsed_samples):
    """
    Reduces a list of parsed resource dicts to their peak (worst-case) values.

    Args:
        parsed_samples (list[dict]): Parsed resource dictionaries, one per sample,
            as produced by `_parse_single_system_resources`.

    Returns:
        dict: A single parsed resource dictionary holding the peak value of each
            metric across all samples.
    """

    devices = set()
    for p in parsed_samples:
        devices.update(p['gpu'].keys())

    return {
        "cpu": {
            "used_pct": max(p['cpu']['used_pct'] for p in parsed_samples)
        },
        "memory": {
            "total_gb": max(p['memory']['total_gb'] for p in parsed_samples),
            "used_gb": max(p['memory']['used_gb'] for p in parsed_samples),
            "free_gb": min(p['memory']['free_gb'] for p in parsed_samples),
            "used_pct": max(p['memory']['used_pct'] for p in parsed_samples)
        },
        "storage": {
            "total_gb": max(p['storage']['total_gb'] for p in parsed_samples),
            "used_gb": max(p['storage']['used_gb'] for p in parsed_samples),
            "free_gb": min(p['storage']['free_gb'] for p in parsed_samples),
            "used_pct": max(p['storage']['used_pct'] for p in parsed_samples)
        },
        "gpu": {
            device: {
                "compute_used_pct": max(
                    p['gpu'].get(device, {}).get('compute_used_pct', 0) for p in parsed_samples
                ),
                "memory_used_pct": max(
                    p['gpu'].get(device, {}).get('memory_used_pct', 0) for p in parsed_samples
                )
            }
            for device in devices
        }
    }


def print_system_resources(parsed, wg_name):
    """
    Prints the parsed resource dictionary.

    Args:
        parsed (dict): Parsed resource dictionary from `parse_system_resources`.
        wg_name (str): Workgroup display name to show in the summary header.

    Returns:
        None
    """
    print(f"=== Resource Summary for Workgroup: {wg_name} ===")
    print(f"  CPU Used:          {parsed['cpu']['used_pct']}%")
    print(f"  Memory Used:       {parsed['memory']['used_gb']} GB / {parsed['memory']['total_gb']} GB ({parsed['memory']['used_pct']}%)")
    print(f"  Storage Used:      {parsed['storage']['used_gb']} GB / {parsed['storage']['total_gb']} GB ({parsed['storage']['used_pct']}%)")
    for device, metrics in parsed['gpu'].items():
        print(f"  GPU ({device}) Compute: {metrics['compute_used_pct']}%")
        print(f"  GPU ({device}) Memory:  {metrics['memory_used_pct']}%")


def check_resource_thresholds(
    parsed,
    cpu_threshold=None,
    ram_free_gb_threshold=None,
    gpu_threshold=None,
    gpu_memory_threshold=None
):
    """
    Checks whether node resources meet specified thresholds. Any threshold left as
    None is skipped entirely - that metric isn't checked at all, rather than treated
    as "no limit".

    Args:
        parsed (dict): Parsed resource dictionary from `parse_system_resources`.
        cpu_threshold (float): Max allowable CPU usage (%).
        ram_free_gb_threshold (float): Minimum required free RAM (GB).
        gpu_threshold (float): Max allowable GPU compute usage (%) - at least one device must meet this.
            If set to a nonzero value and no GPU is present, the check will fail.
        gpu_memory_threshold (float): Max allowable GPU memory usage (%) - at least one device must meet this.
            NOTE: this is a usage PERCENTAGE, not a GB value - the platform doesn't expose absolute
            VRAM capacity, only percent-used, so an absolute free-GB threshold isn't possible here.
            If set to a nonzero value and no GPU is present, the check will fail.

    Returns:
        dict: {
            "passed": bool - True only if every threshold provided was satisfied,
            "failures": list[dict] - one entry per threshold that was NOT satisfied (empty if
                passed is True). Each entry has "metric", "actual", "threshold", and a
                human-readable "detail" string explaining the failure and by how much.
        }
    """
    failures = []

    if cpu_threshold is not None:
        actual = parsed['cpu']['used_pct']
        if actual > cpu_threshold:
            over_by = round(actual - cpu_threshold, 2)
            failures.append({
                "metric": "CPU usage",
                "actual": actual,
                "threshold": cpu_threshold,
                "detail": (
                    f"CPU usage peaked at {actual}%, {over_by} percentage points over the "
                    f"{cpu_threshold}% limit."
                ),
            })

    if ram_free_gb_threshold is not None:
        actual = parsed['memory']['free_gb']
        if actual < ram_free_gb_threshold:
            short_by = round(ram_free_gb_threshold - actual, 2)
            failures.append({
                "metric": "Free RAM",
                "actual": actual,
                "threshold": ram_free_gb_threshold,
                "detail": (
                    f"Only {actual} GB RAM free at the worst sampled moment, {short_by} GB "
                    f"short of the {ram_free_gb_threshold} GB required."
                ),
            })

    has_gpu = bool(parsed['gpu'])

    # A threshold of exactly 0 is treated the same as None (no GPU requirement) -
    # this lets "leave the default" and "explicitly say I don't need a GPU" both work
    # without forcing a fail on GPU-less workgroups. If you actually want to require
    # 0% GPU usage, this won't enforce that - only nonzero thresholds are enforced.
    gpu_required = (gpu_threshold is not None and gpu_threshold != 0) or \
                   (gpu_memory_threshold is not None and gpu_memory_threshold != 0)

    if gpu_required and not has_gpu:
        failures.append({
            "metric": "GPU availability",
            "actual": "no GPU",
            "threshold": "at least one GPU device",
            "detail": (
                "gpu_threshold and/or gpu_memory_threshold was set, but this workgroup has "
                "no GPU at all."
            ),
        })
    else:
        if gpu_threshold is not None and has_gpu:
            best_device, best_value = min(
                ((d, m['compute_used_pct']) for d, m in parsed['gpu'].items()),
                key=lambda item: item[1],
            )
            if best_value > gpu_threshold:
                over_by = round(best_value - gpu_threshold, 2)
                failures.append({
                    "metric": "GPU compute usage",
                    "actual": best_value,
                    "threshold": gpu_threshold,
                    "detail": (
                        f"Every GPU device is over the {gpu_threshold}% compute limit; the "
                        f"closest, {best_device}, peaked at {best_value}% ({over_by} "
                        f"percentage points over)."
                    ),
                })

        if gpu_memory_threshold is not None and has_gpu:
            best_device, best_value = min(
                ((d, m['memory_used_pct']) for d, m in parsed['gpu'].items()),
                key=lambda item: item[1],
            )
            if best_value > gpu_memory_threshold:
                over_by = round(best_value - gpu_memory_threshold, 2)
                failures.append({
                    "metric": "GPU memory usage",
                    "actual": best_value,
                    "threshold": gpu_memory_threshold,
                    "detail": (
                        f"Every GPU device is over the {gpu_memory_threshold}% memory limit; "
                        f"the closest, {best_device}, peaked at {best_value}% ({over_by} "
                        f"percentage points over)."
                    ),
                })

    return {"passed": not failures, "failures": failures}
