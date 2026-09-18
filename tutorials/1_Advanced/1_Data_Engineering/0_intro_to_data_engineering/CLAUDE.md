# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Commands

```bash
# Create and activate virtual environment
python3 -m venv .venv/rhino_data_engineering
source .venv/rhino_data_engineering/bin/activate

# Install dependencies (run from this directory)
pip install -r requirements.txt

# Register as Jupyter kernel (required for notebook execution)
python -m ipykernel install --user --name rhino_data_engineering --display-name "rhino_data_engineering"

# Launch notebooks
jupyter notebook    # or: jupyter lab

# Run a notebook non-interactively
jupyter nbconvert --to notebook --execute <notebook>.ipynb --output <notebook>_executed.ipynb
```

---

## Architecture

This is an **8-part sequential tutorial** demonstrating a complete data engineering workflow on the Rhino FCP. Each tutorial folder contains a `README.md` with instructions and an `.ipynb` orchestration notebook. Tutorials must be completed in order — each one produces outputs (dataset UIDs, schema UIDs) consumed by the next.

### Data Flow

```
data/*.csv  →  Tutorial 1 (Register)  →  Tutorial 2 (Discover)  →  Tutorial 3 (Prepare)
                                                                          ↓
Tutorial 5 (Validate)  ←  Tutorial 4 (Harmonize → OMOP)  ←  Cleaned Datasets
     ↓
Tutorial 6 (Feature Engineering)  →  Patient-level feature table
```

Tutorial 7 (Rhino MCP) is a standalone alternative path that reproduces tutorials 1–6 via Claude Desktop + natural language.

### Rhino FCP Execution Model

All computation runs **on the Rhino client node** (on-prem or managed cloud). The orchestration notebooks run locally and use the Rhino SDK to issue API calls to the FCP cloud, which then dispatches jobs to the client. Raw data never leaves the client network.

- **Notebooks** = orchestration layer (SDK calls, result inspection)
- **Code Objects** = scripts that execute inside isolated containers on the client node
- **Federated metrics** = aggregate-only queries (count, mean, histogram, null rate) — no row-level data returned

### Key SDK Patterns

**Authentication**
```python
import rhino_health as rh
session = rh.login(username="...", password=getpass())
# Non-prod: add rhino_api_url=ApiEnvironment.DEV1_AWS_URL
```

**Required UIDs** — Retrieved from the FCP Dashboard (3-dot menu → Copy UID)
- `PROJECT_UID` — Projects page
- `WORKGROUP_UID` — Settings → Primary Workgroup
- Dataset/Schema UIDs — Datasets / Data Schemas pages

**Import path (common mistake)**
```python
# CORRECT
from rhino_health.lib.metrics import Count, Mean, Histogram, NullRate
from rhino_health.lib.endpoints.code_object.code_object_dataclass import CodeObjectCreateInput
# WRONG — missing .lib
from rhino_health.metrics import Mean
```

### Tutorial-Specific Patterns

**Tutorial 1 — Dataset Registration**
- `session.dataset.add_dataset(DatasetCreateInput(...))` — registers a CSV path on the client (no upload)
- `session.data_schema.generate_data_schema_from_dataset(...)` — infers column types from a sample
- Auto-generated schemas frequently misclassify dates as `STRING` and nullable integers as `FLOAT` — always review and correct before proceeding

**Tutorial 2 — Data Discovery**
- `dataset.get_metric(Count())`, `dataset.get_metric(Histogram("column"))` — per-dataset federated metrics
- `session.sql_query.execute_query(...)` — federated SQL returning aggregate results as a pandas DataFrame
- Federated datasets combine multiple site datasets: `session.dataset.add_federated_dataset(FederatedDatasetCreateInput(...))`

**Tutorial 3 — Data Preparation via Code Objects**
- Code Object scripts run in isolated containers: input at `/input/dataset.csv`, output to `/output/dataset.csv`
- Multiple inputs use indexed paths: `/input/0/dataset.csv`, `/input/1/dataset.csv`
- Runtime parameters available at `/input/run_params.json`
- **The Rhino SDK is unavailable inside Code Object scripts** — only pandas, numpy, stdlib

**Tutorial 4 — OMOP Harmonization**
Harmonization requires four sequential steps — each must complete before the next:
1. `session.harmonization.analyze(...)` — checks column alignment between source schema and OMOP target
2. `session.harmonization.setup_mapping(...)` — creates syntactic + semantic mapping objects
3. `session.semantic_mapping.approve(...)` — human review of value-level mappings (e.g., `"Male"` → concept ID `8507`); must reach `Approved` status
4. `session.syntactic_mapping.auto_generate(...)` — auto-populates field transformation rules
5. `session.syntactic_mapping.run(...)` — executes the full transformation

Two mapping layers:
- **Semantic mapping** — value translation (source term → OMOP concept ID); requires explicit approval per entry
- **Syntactic mapping** — structural transformation (column rename, type cast, date format, vocabulary lookup, expression)

**Tutorial 5 — Validation**
Validation is done entirely through federated metrics and SQL — no raw data is returned. Checks cover: null rates on required fields, concept ID distributions against valid OMOP sets, referential integrity across tables, and row count reconciliation.

**Tutorial 6 — Rhino MCP**
The MCP server wraps the Rhino SDK as Claude tools. Configure in `~/.config/claude/claude_desktop_config.json` with `RHINO_USERNAME`, `RHINO_PASSWORD`, `RHINO_ENVIRONMENT`. The notebook documents prompt → tool mappings for reproducing the full workflow conversationally.

---

## Parent Repository Context

See `/solutions/CLAUDE.md` for broader team standards (code style, security requirements, commit practices) and federated learning / NVFlare containerization patterns. This tutorial focuses on data engineering (registration → discovery → preparation → harmonization → validation) and does not cover model training or FL.
