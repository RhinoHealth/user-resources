# Tutorial 0 — Getting Data Onto the Rhino Client

> **You may skip this tutorial if your data files are already on your Rhino client.**
> See [Step 1](#step-1-check-your-data) below.

This tutorial covers how to transfer the example CSV files to your Rhino Client, so they can be registered in Tutorial 1.

# Understanding Where Data Lives

The Rhino Client exposes a filesystem that Code Objects and Dataset Registration uses. Your administrator will tell you which directory has been designated for input data — typically something like `/rhino_data/`

If you're using client-mounted storage, the path may look more like this: `/rhino_data/external/s3/` or `/rhino_data/external/gcp3` (Find this path by going to Settings, via the gear icon, and then clicking on the Client Mounted Storage tab)

When you register a dataset in Tutorial 1, you always provide the **exact** path to the data (e.g., `/rhino_data/external/s3/intro_to_data_engineering/patients.csv`)

## Code Object Path Convention

**NOTE:** When Code Objects run in Tutorial 3, they read from standard paths like `/input/dataset.csv` (if single input) or `/input/0/dataset.csv`, `/input/1/dataset.csv` (multiple inputs). 

> These paths are **automatically managed** by the Rhino Client when you execute a Code Run — you do not copy files there manually.

| Scenario | Input Path | Output Path |
|---|---|---|
| **Single input dataset** | `/input/dataset.csv` | `/output/dataset.csv` |
| **Multiple input datasets (slot 0)** | `/input/0/dataset.csv` | `/output/0/dataset.csv` |
| **Multiple input datasets (slot 1)** | `/input/1/dataset.csv` | `/output/1/dataset.csv` |

In this workflow, each Code Object takes **one input**, so files will be at `/input/dataset.csv`. The path conventions are handled automatically by the Rhino agent — your script just reads from `/input/dataset.csv` and writes to `/output/dataset.csv`.

# Step 0: Prerequisites

Before starting this specific tutorial, ensure you have the following:

- The credentials or network access required to transfer files to your Rhino Client
    - Can be done directly or via client-mounted cloud storage 
    - Ask your Rhino administrator if unsure
- The three source CSV files in the `data/` folder of this repository on your local machine

# Step 1: Check Your Data

Before transferring files, confirm they do not already exist on the client by inspecting the storage directly (if you have access) or:

**Via the FCP Dashboard:**
1. Log in via the UI if you haven't already
2. Navigate to **Projects → [Click Your Project to Select It] → Datasets**
3. If datasets named `Patients — Site A`, `Encounters — Site A`, and `Procedures — Site A` already exist with row counts, your data is already present in the client and have already been registered to your project

**Via an Interactive Container (if unsure of the path):**
You can launch a quick Interactive Container (see Tutorial 2 for details) and check whether files exist at expected paths using a shell command like `ls /rhino_data/`.

> If you have verified example data is already present on the Rhino Client, you can skip the remainder of this tutorial

# Step 2: Upload Example Data

Choose the method that matches your client configuration and the access your administrator has provided. We recommend the following, in order:

## Option 2A: Using Client-Mounted Storage
Follow [this guide](https://docs.rhinofcp.com/settings/mounting-storage-to-your-rhino-client) for instructions on how to mount the client-mounted storage of your choice (e.g., AWS S3, GCP Bucket, Azure blob).

Once your client mounted storage is connected, you'll want to copy the example CSV files in [/data](../data) from your local machine into a new folder you create within that mounted storage.

## Option 2B: Using SFTP
Follow [this guide](https://docs.rhinofcp.com/getting-started/quick-start-guide/registering-data-to-your-rhino-federated-computing-platform-fcp-client-using-sftp) for instructions on how to how to connect to your Rhino client via SFTP.

Once you're connected to the client SFTP server, yyou'll want to copy the example CSV files in [/data](../data) from your local machine into a new folder you create on your Rhino client.

**Using bash (CLI):**
```
sftp> cd /rhino_data/intro_to_data_engineering/
sftp> put encounters.csv
sftp> put patients.csv
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

## Option 2C: Importing from SQL Database

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

# Step 3: Verify Example Data

Before proceeding, confirm that all example data is available to your Rhino Client:

- **Option 2A:** Verify that all files are present in the client-mounted storage. You can typically do this through the cloud's UI.
- **Option 2B/C:** Verify that all files were successfully uploaded to your Rhino Client. You can do this by navigating to the folder using cd and listing its contents using ls.

> Make note of the folder path where your data is now stored (e.g., /rhino_data/external/import-external-datasets-dev/user-resource-examples/intro_to_data_engineering/). You'll need this path to register the data in the next tutorial.

Wait until all example data has finished loading completely before continuing to Tutorial 1.


You can also try checking:

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

# Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
