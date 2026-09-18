# Vertical Federated GWAS — Block-Diagonal Logistic Regression

### Client Auto-Detection

A single `client.py` is deployed to both parties.  On startup it inspects the dataset
schema:

- **Phenotype column present, no rs\* columns** → acts as clinical party
- **rs\* columns present, no phenotype column** → acts as genotype party

No separate configuration is required per party.

---

### Federated GWAS (NVFlare orchestration)

#### Round 0 — Initialization

```
Server  ──►  Both parties   task: init, params: {}
Clinical ──► Server         params: { party_type: "clinical" }
Genotype ──► Server         params: { party_type: "genotype", variant_cols: [...] }
```

The server learns which client is which and obtains the variant list from the genotype
party.

---

#### Rounds 0.1–0.2 — Private Set Intersection (PSI)

```
Server  ──►  Both parties   task: psi_hash
                             params: { salt: "<32-byte hex string>" }

Clinical ──► Server         params: { hashes: ["sha256(salt+id)", ...] }
Genotype ──► Server         params: { hashes: ["sha256(salt+id)", ...] }
```

The server generates a fresh random salt (`base64.b64encode(os.urandom(32))`) and sends
it to both parties.  Each party hashes its sample IDs using scrypt
(`hashlib.scrypt(sample_id, salt, n=512, r=8, p=1)`) and returns the base64-encoded
hash set.  The server computes the intersection of both hash sets.

```
Server  ──►  Both parties   task: psi_filter
                             params: { salt: "...", common_hashes: [...] }

Both    ──►  Server         params: {}   (acknowledgement)
```

Each party filters its local data to only the samples whose hashed ID appears in the
intersection, ensuring both parties operate on exactly the same aligned cohort for all
subsequent steps.

> **PSI privacy note:** scrypt is a memory-hard hash function that makes brute-force
> reversal of hashed IDs computationally expensive.  Each party can still infer the size
> of the non-intersection from the difference in hash set sizes, but cannot feasibly
> reverse hashes back to plaintext IDs.  A production deployment would use an
> OPRF-based or Diffie-Hellman PSI protocol to hide set sizes as well.

---

#### Round 1 — Null Model

```
Server  ──►  Clinical   task: fit_null_model, params: {}
Clinical ──► Server     params: { betas_clin_null: [β₀, β₁, ..., β₃] }
```

The clinical party fits logistic regression on clinical features alone (Newton-Raphson,
fully local, zero communication with genotype party).  The resulting betas warm-start
every variant's full model.

---

#### Rounds 2–N — Newton-Raphson Optimisation (all variants per round)

Each Newton-Raphson iteration requires **three sub-rounds**:

**Sub-round A — Genotype computes partial linear predictor**

```
Server  ──►  Genotype   task: partial_z
                         params: { betas_geno_by_variant: { rs_i: β₄, rs_j: β₄, ... } }

Genotype ──► Server     params: {
                           partial_z_geno_by_variant: {
                             rs_i: [z_geno_1, ..., z_geno_N],   ← N_samples floats
                             rs_j: [...],
                             ...
                           }
                         }
```

z\_geno\_i = dosage\_std\_i × β₄\_i  (standardised dosage scaled by current beta)

---

**Sub-round B — Clinical computes z\_total, gradients, residuals**

```
Server  ──►  Clinical   task: clinical_iterate
                         params: {
                           betas_clin_by_variant:     { rs_i: [β₀..β₃], ... },
                           partial_z_geno_by_variant: { rs_i: [...], ... }
                         }

Clinical ──► Server     params: {
                           gradient_clin_by_variant: { rs_i: [∂ℓ/∂β₀..∂ℓ/∂β₃], ... },
                           H_cc_by_variant:          { rs_i: [[4×4 matrix]], ... },
                           residual_by_variant:      { rs_i: [y-p per sample], ... },
                           W_by_variant:             { rs_i: [p(1-p) per sample], ... }
                         }
```

Clinical computes: z\_total = X\_clin @ β\_clin + z\_geno → p = sigmoid(z\_total) → r = y − p

---

**Sub-round C — Genotype computes gradient and Hessian**

```
Server  ──►  Genotype   task: geno_iterate
                         params: {
                           betas_geno_by_variant: { rs_i: β₄, ... },
                           residual_by_variant:   { rs_i: [...], ... },
                           W_by_variant:          { rs_i: [...], ... }
                         }

Genotype ──► Server     params: {
                           gradient_geno_by_variant: { rs_i: ∂ℓ/∂β₄, ... },   ← scalar
                           H_gg_by_variant:          { rs_i: ∂²ℓ/∂β₄², ... }  ← scalar
                         }
```

gradient\_geno = dosage\_std.T @ residual
H\_gg = −(dosage\_std.T × W) @ dosage\_std  (scalar, negative definite)

---

**Server: Newton-Raphson update (block-diagonal)**

For each unconverged variant the server:

1. Clinical block update: `Δβ_clin = (−H_cc)⁻¹ @ gradient_clin`
2. Genotype block update: `Δβ_geno = −gradient_geno / H_gg`
3. Updates: `β_clin ← β_clin + Δβ_clin`, `β_geno ← β_geno + Δβ_geno`
4. Convergence: `‖Δβ_clin‖² + Δβ_geno² < 1×10⁻⁶` — converged variants are dropped

> **Block-diagonal approximation:** The full Newton step requires cross-party Hessian
> terms H\_cg = −X\_clin.T × W × dosage, which would require both parties' data
> simultaneously.  The block-diagonal approximation ignores these cross terms, treating
> each party's parameters as independent for the Newton step.  This is equivalent to
> coordinate-descent in Newton space and converges correctly, requiring approximately
> 15–20 iterations.

---

#### Final Hessian Round

After convergence (or MAX\_ITERATIONS reached), one additional iterate round is sent for
all variants to collect final Hessians for standard error computation.

---

#### Phenotype Relay and Finalisation

```
Server  ──►  Clinical   task: get_phenotype, params: {}
Clinical ──► Server     params: { phenotype: [0, 1, 0, ...] }

Server  ──►  Genotype   task: finalize_gwas
                         params: {
                           variant_cols:     [...],
                           phenotype_vector: [0, 1, 0, ...]
                         }

Genotype ──► Server     params: {
                           stats: {
                             rs_i: {
                               maf_cases, maf_controls,
                               n_cases, n_controls,
                               n_cases_ref, n_cases_alt,
                               n_controls_ref, n_controls_alt
                             }, ...
                           }
                         }
```

See §Privacy for a discussion of the phenotype relay.

---

#### Output Round

```
Server  ──►  Both parties   task: write_output
                             params: { results: { ... } }   ← full results DataFrame

Both ──►  /output/0/.../dataset.csv
```

---

## Data Transmitted Per Round

| Direction | Task | Per-variant payload | Approximate total |
|---|---|---|---|
| Server → Genotype | `partial_z` | 1 float (beta)
| Genotype → Server | `partial_z` | 2000 floats (z\_geno)
| Server → Clinical | `clinical_iterate` | 4 floats (β\_clin) + 2000 floats (z\_geno)
| Clinical → Server | `clinical_iterate` | 4 floats (grad) + 16 floats (H\_cc) + 4000 floats (residual+W)
| Server → Genotype | `geno_iterate` | 1 float (beta) + 4000 floats (residual+W)
| Genotype → Server | `geno_iterate` | 2 scalars (grad + H\_gg)

The dominant payload is sample-level data (residuals and weights) exchanged each
iteration.

---

## Privacy

### What each party shares

| Party | Shares | Does not share |
|---|---|---|
| Clinical | Null model betas, per-variant gradients and Hessians (4-vectors), residuals, weights W, phenotype vector (finalize only) | Raw features, individual labels |
| Genotype | Variant list, per-variant partial z (sample-level), per-variant gradient and Hessian (scalars), MAF statistics | Raw dosage matrix |

### Privacy limitations in this demo

Two items are shared that would require additional protection in production:

1. **Residuals (y − p) and weights W** — forwarded from clinical to genotype each
   iteration.  These are correlated with phenotype labels: a residual of +0.8 indicates
   a case with low predicted probability.  In production, differential-privacy noise or
   secure aggregation should be applied before forwarding.

2. **Phenotype vector** — sent once from clinical to genotype at the finalise step,
   so that the genotype party can compute case/control MAF.  In production this would
   be replaced by a secure inner product (e.g., oblivious RAM or garbled circuits) to
   compute MAF statistics without the genotype party learning individual labels.

---

## Output Metrics

Each tested variant is reported with: `beta`, `se`, `z_stat`, `chi2_stat`, `p_value`, `OR` (and 95% CI bounds), `MAF_cases`, `MAF_controls`, `n_cases`, `n_controls`, `risk_allele`, contingency table allele counts, `p_fdr` (Benjamini-Hochberg), and `gw_significant` flag.

---

## Multiple Testing Correction

Two thresholds applied post-hoc on the server:

- **Genome-wide significance:** p < 5×10⁻⁸
- **Benjamini-Hochberg FDR:** corrected p-values at q < 0.05

---

## Key Design Decisions

### No PCs in the genotype block

PCs are excluded from both parties in this VFL pipeline:

- **PCs in clinical block:** global PCs computed from all variants absorb causal signal
  (variants are regressed out of themselves), producing deflated test statistics.
- **PCs in genotype block:** would require computing PCs from the dosage matrix and
  sharing them with the server, increasing privacy risk.
- **Acceptable trade-off:** the synthetic dataset spans chromosome 22 only and is drawn
  from a homogeneous simulated population; stratification is not a concern for this demo.

### Intercept in the clinical block

The clinical feature matrix is standardised (mean 0, unit variance) before model
fitting.  Without an explicit intercept term, the model is constrained to predict
P = 0.5 at the population mean, which miscalibrates betas when case prevalence ≠ 50%.
The intercept is appended *after* scaling (so it is not itself standardised).

### Zero regularisation

L2 regularisation (λ > 0) inflates standard errors, biasing z-statistics downward and
deflating the genomic inflation factor.  The logistic regression is well-identified
without regularisation on the synthetic data.

