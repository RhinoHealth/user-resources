# Building & Pushing Containers to ECR

This tutorial covers building a Docker image locally and pushing it to your workgroup ECR registry for use in Generalized Compute and NVFlare code objects on the Rhino FCP.

---

## Prerequisites

- Docker installed and running locally
- AWS CLI installed
- ECR credentials retrieved — see [Retrieving SFTP & ECR Credentials](../Retrieving%20SFTP%20%26%20ECR%20Credentials/)

---

## Scripts

| Script | Description |
|---|---|
| [`docker-push.sh`](./docker-push.sh) | Build, tag, and push a Docker image to your workgroup ECR repository |
| [`gc-docker-run.sh`](./gc-docker-run.sh) | Run a Generalized Compute container locally to test before pushing |

See also in [`../../../../rhino-utils/`](../../../../rhino-utils/):

| Script | Description |
|---|---|
| `nvflare-docker-run.sh` | Run an NVFlare container locally |
| `nvflare-docker-run-inference.sh` | Run an NVFlare inference container locally |
| `run_inference.sh` | Run inference locally against a trained model |

---

## Steps

1. Build your Docker image
   ```bash
   docker build -t my-code-object .
   ```

2. Authenticate with ECR — use your credentials from the FCP UI
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr-url>
   ```

3. Tag and push
   ```bash
   bash docker-push.sh <ecr-url>/<workgroup-repo> my-code-object
   ```

4. Test locally before pushing (optional but recommended)
   ```bash
   bash gc-docker-run.sh my-code-object
   ```

---

## Additional resources

- [Retrieving SFTP & ECR Credentials](../Retrieving%20SFTP%20%26%20ECR%20Credentials/)
- [`../../../../rhino-utils/README.md`](../../../../rhino-utils/README.md)
- [docs.rhinohealth.com — Pushing Containers to the ECR](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)
