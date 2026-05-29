# FCP Client Installation & Node Validation

This tutorial covers deploying a Rhino FCP node at your site and validating it is correctly configured before joining a project.

---

## What you will need

- A server or VM meeting the Rhino FCP hardware requirements
- Docker and the AWS CLI installed
- ECR credentials for your workgroup — see [Retrieving SFTP & ECR Credentials](../Retrieving%20SFTP%20%26%20ECR%20Credentials/)
- Network access to the Rhino FCP platform

---

## Site validation notebooks

Use these notebooks to confirm your node is correctly set up and can run both NVFlare and Generalized Compute workloads:

### Life Science validation
Runs a ChemProp federated regression model using NVFlare autocontainer mode on a molecular dataset.

→ [`site-testing-life-science/site-testing.ipynb`](./site-testing-life-science/site-testing.ipynb)
→ [`site-testing-life-science/README.md`](./site-testing-life-science/README.md)

### Financial validation
Runs an XGBoost federated training job using NVFlare on a credit risk dataset.

→ [`site-testing-financial/site-testing.ipynb`](./site-testing-financial/site-testing.ipynb)
→ [`site-testing-financial/README.md`](./site-testing-financial/README.md)

---

## Validation checklist

Before running the notebooks, confirm:

- [ ] Docker is installed and the daemon is running
- [ ] Your node can reach `*.rhinohealth.com` on the required ports
- [ ] ECR credentials are configured and `docker login` succeeds
- [ ] SFTP credentials are configured for data upload
- [ ] GPU drivers are installed (if using GPU-enabled containers)

---

## Additional resources

- [docs.rhinohealth.com — FCP Client Installation](https://docs.rhinohealth.com/hc/en-us/categories/21242964004381)
- [docs.rhinohealth.com — Hardware Configurations](https://docs.rhinohealth.com/hc/en-us/categories/8092574187037)
- [Retrieving SFTP & ECR Credentials](../Retrieving%20SFTP%20%26%20ECR%20Credentials/)
