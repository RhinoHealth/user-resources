# Installation

← set up your local environment, credentials, and node

Everything you need before running any workloads on the Rhino FCP — SDK setup, credential retrieval, node validation, and container tooling.

---

## Tutorials

### [Configuring your Environment & SDK Setup](./Configuring%20your%20Environment%20%26%20SDK%20Setup/)
Install the Rhino Python SDK, configure authentication, set environment variables, and verify connectivity to the FCP.

---

### [Retrieving SFTP & ECR Credentials](./Retrieving%20SFTP%20%26%20ECR%20Credentials/)
Retrieve your SFTP and ECR credentials from the FCP UI. Includes Docker login and credential validation steps.

---

### [FCP Client Installation & Node Validation](./FCP%20client%20installation%20%26%20node%20validation/)
Deploy and validate a Rhino FCP node. Includes site-testing notebooks for both life science and financial use cases.

- [`site-testing-life-science/`](./FCP%20client%20installation%20%26%20node%20validation/site-testing-life-science/) — NVFlare autocontainer site validation (life science)
- [`site-testing-financial/`](./FCP%20client%20installation%20%26%20node%20validation/site-testing-financial/) — NVFlare XGBoost site validation (financial)

---

### [Building & Pushing Containers to ECR](./Building%20%26%20Pushing%20Containers%20to%20ECR/)
Build a Docker image, tag it, and push it to your workgroup ECR registry using rhino-utils scripts.

- [`docker-push.sh`](./Building%20%26%20Pushing%20Containers%20to%20ECR/docker-push.sh)
- [`gc-docker-run.sh`](./Building%20%26%20Pushing%20Containers%20to%20ECR/gc-docker-run.sh)

---

## Additional resources

- [`../../../rhino-utils/`](../../../rhino-utils/) — Docker push, GC run, NVFlare run, S3 upload scripts
- [docs.rhinohealth.com — Configuring your Environment](https://docs.rhinohealth.com/hc/en-us/articles/12385555709085)
- [docs.rhinohealth.com — Quick Start Guide](https://docs.rhinohealth.com/hc/en-us/articles/21067360736541)
