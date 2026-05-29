# Connecting External Data Sources

Import datasets into the Rhino FCP from external storage systems at run time — without copying data into the platform permanently.

---

## Supported sources

### AWS S3

Import files or folders from an S3 bucket as external inputs to a code run.

→ [`Using S3, SQL/runtime_external_files.ipynb`](./Using%20S3%2C%20SQL/runtime_external_files.ipynb)

---

### SQL Databases

Query a SQL database at run time and ingest the results as a dataset.

→ [`Using S3, SQL/sql-data-ingestion.ipynb`](./Using%20S3%2C%20SQL/sql-data-ingestion.ipynb)

---

### GCP Cloud Storage

Import files from a Google Cloud Storage bucket as external inputs to a code run.

*Tutorial coming soon.*
→ [docs.rhinohealth.com — Importing to and Exporting Datasets from Your Network Storage](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)

---

### Azure Blob Storage

Import files from an Azure Blob Storage container as external inputs to a code run.

*Tutorial coming soon.*
→ [docs.rhinohealth.com — Importing to and Exporting Datasets from Your Network Storage](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)

---

### SMB / Network Shares

Import data from an SMB network share mounted on the FCP client.

*Tutorial coming soon.*
→ [docs.rhinohealth.com — Importing to and Exporting Datasets from Your Network Storage](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)

---

## Additional resources

- [`../../../../rhino-utils/upload-file-to-s3.sh`](../../../../rhino-utils/upload-file-to-s3.sh) — upload local files to S3 for use as external data
- [docs.rhinohealth.com — Adding Data to your FCP Client using SFTP](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)
