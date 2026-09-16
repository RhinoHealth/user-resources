# Tutorial 0 — Getting Data Onto the Rhino Client

> **Skip this tutorial if your data files are already on the Rhino client.**
> See [How to Check](#how-to-check-if-your-data-is-already-present) below.

This tutorial covers how to transfer your CSV files to the Rhino client (also called the Rhino agent or edge node) so they can be registered in Tutorial 1.

---

## Prerequisites

- A Rhino client deployed and connected
    - See `Confirm Your Rhino Client Is Running` section in root level [README.md](../README.md)
- The credentials or network access required to transfer files to the client
    - Can be done directly or via client-mounted cloud storage 
    - Ask your Rhino administrator if unsure
- The three source CSV files in the `data/` folder of this repository on your local machine

---

## How to Check if Your Data Is Already Present

Before transferring files, confirm they do not already exist on the client.

**Via the FCP Dashboard:**
1. Log in at [https://dashboard.rhinohealth.com/login](https://dashboard.rhinohealth.com/login)
2. Navigate to **Projects → [Your Project] → Datasets**
3. If datasets named `Patients — Site A`, `Encounters — Site A`, and `Procedures — Site A` already exist with row counts, your data is present — **skip to Tutorial 1**

**Via an Interactive Container (if unsure of the path):**
You can launch a quick Interactive Container (see Tutorial 2 for details) and check whether files exist at expected paths using a shell command like `ls /rhino_data/`.

---

## Understanding Where Data Lives on the Client

The Rhino client exposes a filesystem that Code Objects and dataset registrations use. Your administrator will tell you which directory has been designated for input data — commonly something like `/rhino_data/`

If you're using client-mounted storage, the path may look more like this: `/rhino_data/external/s3/` or `/rhino_data/external/gcp3` (Find this path by going to settings, via the gear icon, and then clicking on the Client Mounted Storage tab)

When you register a dataset in Tutorial 1, you always provide the **exact** path to the data (e.g., `/rhino_data/external/s3/intro_to_data_engineering/patients.csv`)

### Code Object Path Convention

**NOTE:** When Code Objects run in Tutorial 3, they read from standard paths like `/input/dataset.csv` (single input) or `/input/0/dataset.csv`, `/input/1/dataset.csv` (multiple inputs). 

> These paths are **automatically managed** by the Rhino agent — you do not copy files there manually.

| Scenario | Input Path | Output Path |
|---|---|---|
| **Single input dataset** | `/input/dataset.csv` | `/output/dataset.csv` |
| **Multiple input datasets (slot 0)** | `/input/0/dataset.csv` | `/output/0/dataset.csv` |
| **Multiple input datasets (slot 1)** | `/input/1/dataset.csv` | `/output/1/dataset.csv` |

In this workflow, each Code Object takes **one input**, so files will be at `/input/dataset.csv`. The path conventions are handled automatically by the Rhino agent — your script just reads from `/input/dataset.csv` and writes to `/output/dataset.csv`.

---

## Methods for Getting Data Onto the Client

Choose the method that matches your client configuration and the access your administrator has provided.

### Method 1 — Network / Client Storage Mount (Recommended)

If your client is configured with a shared network storage location (NFS share, SMB/CIFS mount, or cloud object storage mount like AWS S3 or GCP buckets), you can copy files directly using standard filesystem operations.

```bash
# If the network share is mounted at /mnt/rhino-data on your machine:
cp data/patients.csv   /mnt/rhino-data/source/
cp data/encounters.csv /mnt/rhino-data/source/
cp data/procedures.csv /mnt/rhino-data/source/
```

The Rhino client can read from this mount as if files are local. Ask your administrator for the exact mount path and access instructions.

For more info on client-mounted storage, see documentation [here](https://docs.rhinohealth.com/hc/en-us/articles/25630326465693-Mounting-Storage-to-Your-Rhino-Client)

### Method 2 — Import from SQL Database

If your data lives in a relational database (e.g., Epic, Cerner, Redshift, BigQuery, Snowflake) accessible from the Rhino client's network, you can import it directly as a dataset without creating a CSV first.

This uses the Rhino SDK's SQL import capability:

```python
import rhino_health as rh
from getpass import getpass

my_username = "my_email@example.com"  # REPLACE
session = rh.login(username=my_username, password=getpass())

# Import a SQL query result directly as a new FCP dataset
dataset = session.dataset.import_dataset_from_sql(
    project_uid="<YOUR_PROJECT_UID>",
    workgroup_uid=project.primary_workgroup_uid,
    name="Patients — Site A",
    sql_query="SELECT * FROM ehr.patients WHERE cohort_flag = 1",
    connection_string="postgresql://user:password@db-host:5432/ehr_db",
)
print(f"Imported dataset: {dataset.uid}")
```

See the [Rhino SDK documentation on SQL import](https://docs.rhinohealth.com/hc/en-us/articles/34425969191581) for supported database types and connection string formats.


### Method 3 — Direct SFTP

SFTP (Secure File Transfer Protocol) is a method for transferring files from one's local environment directly onto the client edge node. This works for most client configurations.

Instructions can be found [here](https://docs.rhinohealth.com/hc/en-us/articles/11386174986397-How-can-I-import-data-in-my-local-environment-onto-my-Rhino-FCP-client-using-SFTP)

**Using the command line (macOS/Linux/Windows with OpenSSH):**
```bash
sftp rhinosftp@RHINO_CLIENT_IP_ADDRESS

# Once connected, navigate to the data directory and upload:
sftp> cd /rhino_data/intro_to_data_engineering/
sftp> put patients.csv
sftp> put encounters.csv
sftp> put procedures.csv
sftp> ls -lh          # confirm the files are there
sftp> exit
```

**Using FileZilla (GUI, any OS):**
1. Download [FileZilla](https://filezilla-project.org/)
2. Open **File → Site Manager → New Site**
3. Set Protocol: SFTP, Host: `<CLIENT_HOSTNAME>`, Port: `<PORT>`
4. Enter your username and password
5. Connect → navigate to `/data/source/` in the remote panel
6. Drag and drop the three CSV files from your local panel to the remote panel

**Using WinSCP (Windows):**
1. Download [WinSCP](https://winscp.net)
2. Create a new session: File Protocol = SFTP, host, port, credentials
3. Connect → navigate to the target directory → drag and drop files

---

## Verifying the Transfer

After transferring files, verify they are accessible before proceeding to Tutorial 1.

**Via the FCP Dashboard:**
- Navigate to **Workgroups → [Your Workgroup] → Status**
- The agent should be green / connected

**Via SSH (if you have access):**
```bash
ssh <USERNAME>@<CLIENT_HOSTNAME>
ls -lh /rhino_data/intro_to_data_engineering/
# Expected output:
# -rw-r--r-- 1 rhino rhino  12K  patients.csv
# -rw-r--r-- 1 rhino rhino   8K  encounters.csv
# -rw-r--r-- 1 rhino rhino  14K  procedures.csv
```

**Via a test dataset registration:**

A quick way to confirm is to attempt a dataset registration in Tutorial 1. If the path is wrong, you will immediately get an error saying the agent cannot find the file.

---

## What to Note for Tutorial 1

Once your files are on the client, record the **full absolute paths** you used. You will paste these into the Configuration cell of Tutorial 1:

```
ENCOUNTERS_PATH = "/rhino_data/intro_to_data_engineering/encounters.csv"
PATIENTS_PATH   = "/rhino_data/intro_to_data_engineering/patients.csv"
PROCEDURES_PATH = "/rhino_data/intro_to_data_engineering/procedures.csv"
```

---

## Checking Your Work in the FCP Dashboard

After transferring files and before running Tutorial 1:

1. Confirm your agent node is "Online"
2. If you used **"Method 4 — Direct Upload via the FCP Dashboard"** — check **Projects → [Your Project] → Datasets** to confirm the datasets appear
3. If you used **SFTP or network storage** — you will confirm file accessibility implicitly when Tutorial 1's registration cells run successfully

---

## Helpful Links

| Resource | Description |
|---|---|
| [Rhino FCP Dashboard](https://dashboard.rhinohealth.com/login) | Log in here to check workgroup/agent status |
| [Rhino SFTP Guide](https://docs.rhinohealth.com/hc/en-us/articles/12385912890653) | Official SFTP data transfer documentation |
| [Client Mounted Storage](https://docs.rhinohealth.com/hc/en-us/articles/25630326465693-Mounting-Storage-to-Your-Rhino-Client) | Instructions for mounting differnet kinds of storage |
| [Network Storage Import / Export](https://docs.rhinohealth.com/hc/en-us/articles/18246660924061) | Guide for importing/exporting via network storage mounts |
| [SQL Import Guide](https://docs.rhinohealth.com/hc/en-us/articles/34425969191581) | Importing datasets directly from a SQL database |
| [Importing via Dashboard UI](https://docs.rhinohealth.com/hc/en-us/articles/31357028507165) | Step-by-step guide for uploading through the web interface |

---

## Getting Help

For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com)
