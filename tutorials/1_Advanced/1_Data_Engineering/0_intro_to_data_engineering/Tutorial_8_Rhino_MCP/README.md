# Tutorial 8 — The Rhino MCP: AI-Assisted Data Engineering

This tutorial introduces the **Rhino MCP Server** — a cloud-hosted bridge that lets AI assistants like Claude interact with the Rhino FCP in natural language. Everything accomplished in Tutorials 1–7 via SDK notebook calls can also be done through conversational prompts in any MCP-compatible AI client.

No local server to install. No credentials in config files. Setup takes under 5 minutes.

## Overview

The Rhino MCP Server connects any AI assistant directly to the Rhino Federated Computing Platform. Through natural language, you can run federated analytics, explore datasets, execute code, and monitor jobs — all without raw data ever leaving your sites.

The MCP server exposes 8 capability areas, each mapped to a set of named tools your AI assistant can invoke automatically:

| Capability Area | What You Can Do |
|---|---|
| **Authentication** | Login, confirm identity, verify connectivity |
| **Projects** | List, inspect, create, and delete federated projects |
| **Datasets** | Register, sync, profile, compare, and delete datasets — including federated datasets spanning multiple sites |
| **Queries** | Run mean, Kaplan-Meier, Cox PH, Table 1, chi-square, SQL, and more via a single unified tool |
| **Execution** | Upload Python code objects, execute them across sites, launch NVFlare training jobs |
| **Monitoring** | Check run status, stream logs, list recent runs, halt jobs |
| **Collaboration** | List, invite, and remove collaborators; check site connectivity and workgroup status |
| **Harmonization** | Manage schemas, browse vocabularies, apply semantic and syntactic mappings, run full pipelines |

All results are aggregated — raw patient data never leaves hospital sites.

## How Authentication Works

The Rhino MCP Server uses **OAuth 2.1 with PKCE** — the same standard used by Google and GitHub. You never put credentials in a config file.

```
1. Add the MCP server URL to your AI client
2. On first use, your browser opens automatically for Rhino FCP login
3. A secure token is issued and stored by your AI client
4. All subsequent tool calls use the token automatically
```

Your credentials never appear in the AI chat. The AI assistant never sees your password.

---

## Setup

### Default Environment: Production

The production MCP server URL is:

```
https://mcp.rhinohealth.com/mcp
```

Use this unless you've been told to use a different environment. Choose your AI client below.

---

### Option A: Claude Desktop (Simplest)

1. Open Claude Desktop → click your username (bottom left) → **Settings → Connectors**
   (or click **Customize → Connectors**)
2. Click **+** → **Add custom connector**
3. Enter:
   - **Name:** `Rhino FCP`
   - **URL:** `https://mcp.rhinohealth.com/mcp`
4. Click **Save**, then **Connect**
5. A browser window opens — log in to Rhino FCP. Done.

---

### Option B: Claude Code CLI

```bash
# Add the server (user scope = available in all projects)
claude mcp add \
  --transport http \
  --scope user \
  rhino-health \
  https://mcp.rhinohealth.com/mcp

# Verify it's registered
claude mcp list

# Start Claude and authenticate
claude
> "List my Rhino FCP projects"
# Browser opens for OAuth login on first use
```

No config file needed — everything is managed via the CLI.

---

### Option C: Claude Desktop (Dev Mode / Config File)

If you prefer editing the config file directly (e.g., for scripting or CI):

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rhino-health": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.rhinohealth.com/mcp"
      ]
    }
  }
}
```

> **Prerequisite:** Node.js v18+ must be installed (`npx` must be on PATH).
> Install via `brew install node` (macOS) or from nodejs.org.

Quit Claude Desktop fully (**Cmd+Q**) and reopen. On first use, ask: `"List my Rhino FCP projects"` — your browser opens for OAuth login.

---

### Option D: Cursor IDE

Create or edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project):

```json
{
  "mcpServers": {
    "rhino-health": {
      "url": "https://mcp.rhinohealth.com/mcp"
    }
  }
}
```

Restart Cursor, open Agent mode (**Cmd+L**), and ask: `"List my Rhino FCP projects"`.

---

### Option E: VS Code + Copilot

Create `.vscode/mcp.json` in your workspace root (or use Command Palette → **MCP: Open Workspace Folder MCP Config**):

```json
{
  "servers": {
    "rhino-health": {
      "type": "http",
      "url": "https://mcp.rhinohealth.com/mcp"
    }
  }
}
```

Restart VS Code. Open Copilot Chat (**Ctrl+Shift+I**) and switch to Agent mode.

> Requires VS Code 1.99+ with an active GitHub Copilot subscription.

---

## Switching Environments

Each environment has its own MCP URL. To switch, replace the URL in your config with the one for your target environment and re-authenticate.

| Environment | URL |
|---|---|
| **prod (AWS)** — default | `https://mcp.rhinohealth.com/mcp` |
| prod (GCP) | `https://mcp.rhinofcp.com/mcp` |
| prod-us2 (GCP) | `https://mcp-prod-us2.rhinofcp.com/mcp` |
| solutions (GCP) | `https://mcp-solutions.rhinofcp.com/mcp` |
| staging (AWS) | `https://mcp-staging.rhinohealth.com/mcp` |
| staging (GCP) | `https://mcp-staging.rhinofcp.com/mcp` |
| qa-cloud (AWS) | `https://mcp-qa-cloud.rhinohealth.com/mcp` |
| qa-cloud (GCP) | `https://mcp-qa-cloud.rhinofcp.com/mcp` |
| dev1 (AWS) | `https://mcp-dev1.rhinohealth.com/mcp` |
| dev1 (GCP) | `https://mcp-dev1.rhinofcp.com/mcp` |
| dev2 (GCP) | `https://mcp-dev2.rhinofcp.com/mcp` |
| dev3 (GCP) | `https://mcp-dev3.rhinofcp.com/mcp` |
| dev5 (GCP) | `https://mcp-dev5.rhinofcp.com/mcp` |
| dev6 (GCP) | `https://mcp-dev6.rhinofcp.com/mcp` |
| demo (AWS) | `https://mcp-demo.rhinohealth.com/mcp` |
| demo-dev (AWS) | `https://mcp-demo-dev.rhinohealth.com/mcp` |

**Example — switching Claude Code CLI to dev1:**

```bash
# Remove the existing entry and re-add with the dev1 URL
claude mcp remove rhino-health
claude mcp add \
  --transport http \
  --scope user \
  rhino-health \
  https://mcp-dev1.rhinohealth.com/mcp
```

**Verify your connection:**

```bash
curl https://mcp.rhinohealth.com/health
# → {"status":"ok","version":"1.0.0"}
```

---

## Verify Your Setup

Once connected, try these prompts to confirm everything is working:

```
"Who am I on Rhino FCP?"        → confirms identity and permissions
"List my projects"                  → shows accessible projects
"What datasets are in [project]?"   → explores a specific project
```

---

## Tutorial Contents

See [`notebooks/rhino_mcp.ipynb`](./notebooks/rhino_mcp.ipynb) for a reference of prompt → tool mappings for each workflow step.

### Workflow at a Glance

```
Open your AI client
     ↓
Connect and verify access   ("What projects do I have at Rhino?")
     ↓
Register datasets           ("Register patients.csv as a dataset in my project")
     ↓
Generate schemas            ("Auto-generate a schema for the patients dataset")
     ↓
Discover data               ("What's the gender distribution in the patients dataset?")
     ↓
Run data prep               ("Create and run a Python code object that cleans...")
     ↓
Set up harmonization        ("Analyze the patients dataset against the OMOP Person schema")
     ↓
Approve terms               ("Approve the gender mapping: Male → 8507, Female → 8532")
     ↓
Run harmonization           ("Run the harmonization for the patients → OMOP Person mapping")
     ↓
Verify output               ("How many rows are in the harmonized Person table?")
     ↓
Engineer features           ("Create a generalized compute code object that joins the OMOP
                              Person, Visit, and Procedure tables into a patient feature table,
                              and pass the script as a run parameter")
     ↓
Verify feature table        ("How many patients are in the feature table? What's the mean age?")
     ↓
Select cohorts              ("Create a generalized compute code object that filters the feature
                              table to male patients aged 30-40, and run it")
     ↓
Verify cohorts              ("How many patients are in the Males 30-40 cohort?
                              What's the mean age?")
```

---

## Tool Reference

The Rhino MCP exposes the following capabilities. Your AI client selects the appropriate tool automatically based on your prompt.

| What You Say | Tool |
|---|---|
| "What projects do I have?" | `rhino_project_list` |
| "Register patients.csv as a dataset" | `rhino_dataset_create` |
| "Generate a schema for this dataset" | `rhino_data_schema_create` |
| "What's the gender distribution?" | `rhino_metric_run` |
| "Profile the encounters dataset" | `rhino_dataset_profile` |
| "Compare encounters at Site A and Site B" | `rhino_dataset_compare` |
| "Create a Python code object that..." | `rhino_code_object_create` |
| "Run the prep code object on all three datasets" | `rhino_code_run` |
| "Is my run finished?" | `rhino_run_get_status` |
| "Analyze patients against OMOP Person schema" | `rhino_harmonization` (analyze) |
| "Set up the harmonization mapping" | `rhino_harmonization` (setup_mapping) |
| "Show me the proposed gender term matches" | `rhino_semantic_mapping` (get_data) |
| "Approve the gender mapping" | `rhino_semantic_mapping` (approve) |
| "Auto-generate the syntactic mapping fields" | `rhino_syntactic_mapping` (auto_generate) |
| "Run the harmonization" | `rhino_syntactic_mapping` (run) |
| "What vocabularies are available?" | `rhino_vocabulary` (list) |
| "Create a generalized compute code object that joins the OMOP tables into a feature table" | `rhino_code_object_create` |
| "Run the feature engineering code object on the OMOP datasets" | `rhino_code_run` |
| "How many patients are in the feature table?" | `rhino_metric_run` |
| "Create a generalized compute code object that filters the feature table to males aged 30-40" | `rhino_code_object_create` |
| "Run the cohort selection code object against the Patient Features dataset" | `rhino_code_run` |
| "How many patients are in the Males 30-40 cohort? What's the mean age?" | `rhino_metric_run` |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Browser doesn't open for login | Check default browser settings; fully restart your AI client |
| Server not responding / timeout | Verify the URL ends with `/mcp`; run the `curl` health check above |
| Invalid Host / 421 error | Ensure the full `https://` URL is included; update `mcp-remote` to latest (`npx -y mcp-remote@latest`) |
| OAuth succeeds but tools fail | Restart client for a fresh OAuth token; verify project permissions in the FCP dashboard |
| `NOT_AUTHENTICATED` error | Token expired — restart your AI client to trigger a new login |
| Tools appear but return no data | Confirm project access in the Rhino platform; check that your account has workgroup membership |

Need help? Contact [support@rhinofcp.com](mailto:support@rhinofcp.com) with your client name, error message, and the output of the health check curl command.

---

## Tips

- **Be specific with dataset names.** The MCP resolves datasets by name — include enough context (e.g., "the prepared patients dataset" vs. "the raw patients dataset") if multiple datasets have similar names.
- **Approval is still your responsibility.** Claude can display proposed semantic mapping terms and execute approval instructions based on user-provided input/output data schema descriptions (if no descriptions provided, the user will get an internal error), but reviewing these recommendations for clinical correctness remains a human task. Currently, this review process cannot be accomplished via the API/SDK/MCP and must be performed through the UI.
- **All operations are still federated.** The MCP does not change the privacy model — raw data never leaves sites regardless of whether you use the SDK or the MCP.
- **To disconnect:** remove the `rhino-health` entry from your config (or run `claude mcp remove rhino-health`) and restart your client.
