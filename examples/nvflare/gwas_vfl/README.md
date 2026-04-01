# Vertical Federated GWAS Demo

Vertical federated learning is a form of federated learning where multiple sites hold data on the same sample space but possess different information of these samples. For example, one site holds target labels while another holds the feature space, or both parties hold different portions of the feature space.

This document describes the vertical federated genome-wide association study (GWAS)
pipeline implemented across two data parties.  The analysis identifies genetic variants
associated with schizophrenia using logistic regression optimised via a federated
Newton-Raphson procedure.  Raw patient data never leaves each party — only aggregated
statistical quantities are transmitted. The exact implementation of this VFL algorithm 
can be found in [`nvflare/IMPLEMENTATION.MD`](nvflare/IMPLEMENTATION.MD).

The pipeline identifies genetic variants associated with schizophrenia across two parties — a clinical site holding phenotype and covariate data, and a genomics site holding variant dosages — without either party sharing raw data.

---
## Background

### Vertical Federated Learning

This pipeline uses **vertical** federated learning (VFL): two organisations hold
different *features* for the same patients.

| Party | Data held | Has phenotype? |
|---|---|---|
| Clinical party | age, sex, BMI | **Yes** |
| Genotype party | variant dosages (rs\*\*\* columns) | No |

Private Set Intersection (PSI) aligns sample IDs across parties without revealing
which IDs are not in common.  After alignment, the two parties train a joint logistic
regression model without either party ever sending raw data to the other.

### Why VFL for GWAS?

In real-world biobanks, clinical records and genomic data are often held by different
institutions with strict data governance agreements — for example, a hospital system
holding EHR data and a sequencing centre holding genotype arrays.  VFL allows a joint
GWAS without centralising either dataset.

### Why Not Meta-Analysis?

Standard federated GWAS aggregates locally-fit summary statistics (beta + SE per site)
via inverse-variance weighting.  This approximation requires each site to fit a full
logistic regression independently, which in turn requires each site to hold *both*
features and labels.  In the VFL setting this is not possible — the genotype party has
no access to labels.  The gradient and Hessian sharing approach used here computes the
true joint optimum.

---

## Model Specification

A separate logistic regression model is fit for each variant:

```
P(schizophrenia = 1) = logistic(β₀ + β₁·age + β₂·sex + β₃·bmi + β₄·dosage)
```

- **Outcome:** binary schizophrenia phenotype (1 = case, 0 = control)
- **Clinical features (β₀–β₃):** intercept, standardised age/sex/BMI
- **Genotype feature (β₄):** standardised variant dosage (0/1/2 copies of alt allele)
- **Design:** variant beta is always the last coefficient (β₄); clinical betas are
  initialised from a pre-trained null model and refined jointly per variant

---

## Architecture

### Party Roles

```
┌─────────────────────────┐          ┌─────────────────────────┐
│     Clinical Party      │          │     Genotype Party      │
│                         │          │                         │
│      age, sex, bmi,     │          │  rs* dosage columns     │
│  phenotype (cases/ctrls)│          │  (no labels)            │
└─────────┬───────────────┘          └───────────────┬─────────┘
          │                  SERVER                  │
          │             ┌──────────────┐             │
          └────────────►│  Coordinator │◄────────────┘
                        │  (NVFlare)   │
                        └──────────────┘
```

The server coordinates round-trip communication between the two parties.  It never
holds raw features or labels — only the parameter vectors (betas) and intermediate
statistics that both parties have agreed to share.


## Overview

```
gwas_vfl/
├── README.md
├── data/
│   ├── site1_clinical_aggregated_data.csv   # Clinical party: age, sex, BMI, phenotype
│   ├── site2_genomics_data.csv              # Genotype party: rs* variant dosages
│   └── site2_variant_metadata.csv           # Variant annotations (gene, position)
├── results/
│   ├── manhattan_plot.png                   # Gene-coloured Manhattan plot
│   └── qq_plot.png                          # QQ plot with genomic inflation factor
├── nvflare/                                 # NVFlare federated learning container
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── meta.json
│   ├── IMPLEMENTATION.md                    # Full protocol and design documentation
│   └── app/
│       ├── config/
│       │   ├── config_fed_server.json
│       │   └── config_fed_client.json
│       └── custom/
│           ├── server.py                    # VFL GWAS server (orchestration + statistics)
│           └── client.py                    # Unified client (auto-detects party type)
└── visualization/                           # Visualization code object
    ├── Dockerfile
    ├── gwas_visualization.py
    └── requirements.txt
```

## Prerequisites

An active Rhino Health account with access to the platform.

## Contents

### data/

This directory contains the input datasets for both parties.

- **`site1_clinical_aggregated_data.csv`** — uploaded to the clinical party site. Contains `sample_id`, `age`, `sex`, `bmi`, and `phenotype` (1 = schizophrenia case, 0 = control).
- **`site2_genomics_data.csv`** — uploaded to the genomics party site. Contains `sample_id` followed by one column per variant (rs\* identifiers), with values representing allele dosage (0, 1, or 2 copies of the alt allele).
- **`site2_variant_metadata.csv`** — uploaded alongside the genomics data or used as a second input to the visualization code object. Contains `variant_id`, `chromosome`, `position`, and `gene` annotation.

### nvflare/

The NVFlare federated learning container implementing the VFL GWAS protocol.

A single `client.py` is deployed to both party sites. On startup it inspects the dataset schema to determine its role:

- **Phenotype column present, no rs\* columns** → acts as clinical party
- **rs\* columns present, no phenotype column** → acts as genotype party

No separate configuration is required per party.

#### Federated Learning Setup

- **Framework**: NVFlare 2.6.0
- **Algorithm**: Block-diagonal Newton-Raphson (custom, via `BaseFedAvg`)
- **Max rounds**: 100 (early exit on convergence)
- **Clients**: 2 (clinical party + genotype party)

#### Protocol Summary

Each run proceeds through the following phases:

The analysis runs in several coordinated steps between the server and the two data parties. First, the server identifies which party holds clinical data and which holds genetic data. Next, the two parties verify that they are working with the same set of patients by exchanging anonymised, scrambled patient identifiers — no raw IDs are ever shared. Once aligned, the clinical party builds a baseline statistical model using only its own data (age, sex, BMI), which is used as a starting point for the full analysis. The server then runs the main association analysis by passing small statistical summaries back and forth between the two parties in repeated rounds, gradually refining the model for every genetic variant being tested — raw data never leaves either site. Once the results have stabilised, a final round collects the information needed to compute confidence intervals. The genomics party then calculates allele frequency statistics, and the server assembles the complete results and returns them to both parties.

For full protocol details, data volumes, and privacy limitations see [`nvflare/IMPLEMENTATION.MD`](nvflare/IMPLEMENTATION.MD).

#### Data Output

Results are saved to the following dataset:
```
VFL GWAS Results (<Party> Party)
```

### visualization/

A code object that produces a Manhattan plot, QQ plot, and summary statistics from the GWAS results.

**Inputs:**
- Input 0: VFL GWAS Results (<Party> Party) (output of `nvflare` code object)
- Input 1: variant metadata

**Outputs:**
- `manhattan_plot.png` — genome-wide Manhattan plot coloured by gene annotation
- `qq_plot.png` — QQ plot with genomic inflation factor (λ_GC)
- Results csv — top 10 variants by p-value with chart file references

## High Level Instructions
1. Create a project within the Rhino FCP dashboard
2. Upload your data to your client mounted storage
3. Import your data within the project
4. Create the NVFlare and Visualization Code objects in your project
   1. Note the Visualization code object requires two input datasets
5. Run the NVFlare code object
   1. Note you should select both the clinical and genomic datasets as inputs, and then select the box for simulating FL (one client per dataset)
6. Run the visualization code object
7. Export your results for review

## Additional Documentation
[Tutorial 1](https://docs.rhinohealth.com/hc/en-us/articles/8088478664349-Tutorial-1-Basic-Usage) can provide general guidance on importing data within a project and creating the code objects found in this example.

For additional support, please reach out to [support@rhinohealth.com](support@rhinohealth.com)
