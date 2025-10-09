# Code Review Expectations

## Overview and Definitions

- **Branching Strategy:** Creating a consistent branching strategy with **`dev,`** **`test`**, and **`main`** branches helps to streamline clean code integration, minimize errors, and clarify promotion paths through code review processes.  In some scenarios only **`dev,`** and **`main`** may be utilized.
- **Code Reviews:** All proposed changes require peer code review for quality, knowledge sharing, and traceability. Reviews are conducted and documented in GitHub pull requests (PRs).
- **Pull Requests (PRs):** All code changes must be submitted as PRs. PRs record review comments, approvals, and test results before changes can merge into protected branches.

## Branch Structure and Roles

- **dev:** Central branch for all ongoing development. Feature branches must be created from here.
- **test:** Branch for code that has passed peer review and is ready for integration and further testing. Promotion to **`test`** requires additional reviews and tests prior to merging.
- **main:** The production branch. Only deployable, fully reviewed, and approved code is merged here, under strict controls.

## Code Review Etiquette

- Provide constructive, actionable, and respectful feedback.
- Document all decisions and discussions within PRs for audit and improvement.
- Annotate any complex code blocks to aid reviewers.
- Use small, focused PRs (ideally <400 lines of code) for better quality and faster turnaround.

## Branching Workflow

## Feature Work

- Developers create feature or bugfix branches from **`dev`**.
    - Branch names should reference relevant Jira tickets (e.g., **`feature/CDR1900`**, **`bugfix/CDR1750`**).
- When complete, open a PR from the feature branch to the **`dev`** branch.
    - Peer review is required: another engineer (not the author) must review and approve the PR before the code editor merges the PR.
    - All review comments must be documented in GitHub before merging.

## Promotion to Test

- Only the Data Engineering Manager or Cloud Engineer can approve and merge PRs from **`dev`** into **`test`**.
    - Merges to **`test`** must be via PRs, with at least one peer review by someone other than the author.
    - Regular engineers may not push or merge directly to **`test`**.

## Promotion to Main

- Only changes that have passed review/QA in **`test`** may be considered for **`main`**.
- All PRs to **`main`**:
    - Must originate from **`test`**
    - Require at least two approvals: one from another engineer, and a final approval from the CODEOWNER group.
    - Only Data Engineering Manager, Cloud Engineer or System Owner may finalize/merge PRs into **`main`**.
- After deployment, merge changes from **`main`** back into **`dev`** (or the next cycle branch) to keep all lines up to date.

## Hotfixes

- Hotfix branches are created from **`main`** for urgent production issues.
- After verification, merge fixes back into **`main`**, **`dev`**, and **`test`**, ensuring all environments are updated.

# AWS Terraform Infrastructure with Tofu

This directory contains Terraform configuration files for deploying infrastructure on Amazon Web Services (AWS) using [OpenTofu](https://opentofu.org/).

## Prerequisites

- [OpenTofu](https://opentofu.org/) (>= 1.10.x) installed (`brew install opentofu` on macOS)
- [AWS CLI](https://aws.amazon.com/cli/) (>= 2.0.x) installed and configured
- AWS account with sufficient permissions (EC2, IAM, S3, CloudWatch, VPC, CloudTrail, etc.)
- Valid AWS credentials (via `aws configure` or environment variables)

## Setup

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <repo-url>
   cd infrastructure/AWS
   ```

2. **Configure AWS Credentials:**
   You can configure your AWS credentials in one of two ways:

   - **Using the AWS CLI (recommended for most users):**
     ```sh
     aws configure
     ```
     This will prompt you to enter your AWS Access Key, Secret Access Key, region, and output format, and will save them in `~/.aws/credentials` and `~/.aws/config`.

   - **Or by setting environment variables (useful for CI/CD or temporary sessions):**
     ```sh
     export AWS_ACCESS_KEY_ID="<your-access-key>"
     export AWS_SECRET_ACCESS_KEY="<your-secret-key>"
     export AWS_DEFAULT_REGION="<your-region>"  # optional but recommended
     ```

3. **Edit `terraform.tfvars` and create `secret.auto.tfvars`**
   - Set your `aws_region`, `availability_zone`, and other variables as needed in `terraform.tfvars`.
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
     rhino_agent_id                  = "<rhino-provided-agent-id>"
     rhino_package_registry_user     = "<rhino-provided-username>"
     rhino_package_registry_password = "<rhino-provided-password>"
     ```
   - Make sure `secret.auto.tfvars` is listed in `.gitignore` to avoid committing secrets.

4. **(Optional) Configure remote state**
   - Edit `versions.tf` to set your S3 bucket and prefix for state storage if desired.

## Running Tofu

1. **Initialize the working directory:**
   ```sh
   tofu init
   ```

2. **Review the planned changes:**
   ```sh
   tofu plan
   ```

3. **Apply the changes:**
   ```sh
   tofu apply
   ```
   - Review the output and type `yes` to confirm.

4. **(Optional) Destroy resources:**
   ```sh
   tofu destroy
   ```

## Notes
- Ensure you have sufficient service quotas for all resources.
- If you encounter issues destroying S3 buckets (due to remaining objects or versions), you may need to manually empty the buckets before running `tofu destroy`.

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/)
