from pathlib import Path
import base64
import hashlib
import numpy as np
import pandas as pd
import nvflare.client as flare
from sklearn.preprocessing import StandardScaler

# ── Constants (must match server) ─────────────────────────────────────────────
CLINICAL_COLS  = ['age', 'sex', 'bmi']
PHENOTYPE_COL  = 'phenotype'
REGULARIZATION = 0.0
SCRYPT_N       = 512   # iterations (must be power of 2)
SCRYPT_R       = 8
SCRYPT_P       = 1


# ══════════════════════════════════════════════════════════════════════════════
# CLINICAL PARTY  (holds: phenotype, age, sex, bmi)
# ══════════════════════════════════════════════════════════════════════════════

class ClinicalParty:
    """
    Active VFL party — holds phenotype labels and clinical covariates.

    Shares with the server:
      - Null model betas (once, before GWAS)
      - Per-variant gradient and Hessian for clinical betas
      - Per-variant residuals (y - p) and weights w = p(1-p)
      - Phenotype vector for MAF computation (once, at finalize step)

    NOTE: Residuals and weights are correlated with phenotype labels.
    A production deployment would apply secure aggregation before the
    server forwards them to the genotype party.
    """

    def __init__(self, data: pd.DataFrame):
        df = data.copy()
        self._sample_ids = df['sample_id'].tolist()
        self.y = df[PHENOTYPE_COL].values.astype(np.float64)

        scaler   = StandardScaler()
        x_scaled = scaler.fit_transform(df[CLINICAL_COLS].values.astype(np.float64))
        self.x = np.column_stack([x_scaled, np.ones(len(df))])

    def hash_sample_ids(self, salt: str) -> list:
        """Hash sample IDs with shared salt for PSI using scrypt."""
        salt_bytes = base64.b64decode(salt)
        return [
            base64.b64encode(
                hashlib.scrypt(str(sid).encode("utf-8"), salt=salt_bytes,
                               n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
            ).decode("utf-8")
            for sid in self._sample_ids
        ]

    def filter_to_common_samples(self, common_hashes: set, salt: str) -> None:
        """Keep only samples whose hashed ID is in the intersection."""
        salt_bytes = base64.b64decode(salt)
        keep = [
            i for i, sid in enumerate(self._sample_ids)
            if base64.b64encode(
                hashlib.scrypt(str(sid).encode("utf-8"), salt=salt_bytes,
                               n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
            ).decode("utf-8") in common_hashes
        ]
        self.x = self.x[keep]
        self.y = self.y[keep]

    def fit_null_model(self) -> np.ndarray:
        """
        Logistic regression on clinical features only.
        Runs locally — zero communication with the genotype party.
        Used to warm-start each variant's full model.
        """
        betas = np.zeros(self.x.shape[1])
        for _ in range(100):
            z = self.x @ betas
            p = np.clip(1 / (1 + np.exp(-z)), 1e-15, 1 - 1e-15)
            w = p * (1 - p)
            g = self.x.T @ (self.y - p) - REGULARIZATION * betas
            h = -(self.x.T * w) @ self.x - REGULARIZATION * np.eye(len(betas))
            try:
                delta = np.linalg.solve(-h, g)
            except np.linalg.LinAlgError:
                break
            betas += delta
            if np.linalg.norm(delta) < 1e-10:
                break
        return betas

    def clinical_iterate(self, betas_clin_by_variant: dict,
                         partial_z_geno_by_variant: dict) -> dict:
        """
        For each variant, compute z_total = x_clin @ betas_clin + partial_z_geno,
        then return the gradient, Hessian, residuals, and weights for clinical betas.

        gradient_clin[v] = x_clin.T @ (y - p_v)             shape (N_clin,)
        h_cc[v]          = -(x_clin.T * w_v) @ x_clin       shape (N_clin, N_clin)
        residual[v]      = y - p_v                           shape (N_samples,)
        w[v]             = p_v * (1 - p_v)                  shape (N_samples,)
        """
        gradient_clin_bv = {}
        h_cc_bv          = {}
        residual_bv      = {}
        w_bv             = {}

        for v, bc in betas_clin_by_variant.items():
            bc      = np.array(bc, dtype=np.float64)
            z_total = self.x @ bc + np.array(partial_z_geno_by_variant[v], dtype=np.float64)
            p       = np.clip(1 / (1 + np.exp(-z_total)), 1e-15, 1 - 1e-15)
            w       = p * (1 - p)
            r       = self.y - p

            gradient_clin_bv[v] = (self.x.T @ r - REGULARIZATION * bc).tolist()
            h_cc_bv[v]          = (-(self.x.T * w) @ self.x
                                   - REGULARIZATION * np.eye(len(bc))).tolist()
            residual_bv[v]      = r.tolist()
            w_bv[v]             = w.tolist()

        return {
            'gradient_clin_by_variant': gradient_clin_bv,
            'h_cc_by_variant':          h_cc_bv,
            'residual_by_variant':      residual_bv,
            'w_by_variant':             w_bv,
        }


# ══════════════════════════════════════════════════════════════════════════════
# GENOTYPE PARTY  (holds: variant dosages — no labels)
# ══════════════════════════════════════════════════════════════════════════════

class GenotypeParty:
    """
    Passive VFL party — holds variant dosage data, no phenotype labels.

    Shares with the server:
      - Variant column list (once, at init)
      - Partial linear predictor z_geno = dosage_std * beta_geno  (per iteration)
      - Gradient and Hessian for genotype beta                     (per iteration)
      - MAF and contingency statistics                             (at finalize)

    Receives from the server (forwarded from clinical party):
      - Residuals y - p    (per iteration — label-correlated, see privacy note)
      - weights w = p(1-p) (per iteration)
      - Phenotype vector y (once, at finalize — for MAF case/control split)
    """

    def __init__(self, data: pd.DataFrame):
        self.data         = data.reset_index(drop=True)
        self._sample_ids  = data['sample_id'].tolist()
        self.variant_cols = [c for c in data.columns if c.startswith('rs')]

        # Standardize dosage vectors and cache both raw and standardized
        self._dosage_std = {}
        self._dosage_raw = {}
        for v in self.variant_cols:
            raw = data[v].values.astype(np.float64)
            std = raw.std()
            self._dosage_std[v] = (raw - raw.mean()) / std if std > 0 else raw - raw.mean()
            self._dosage_raw[v] = raw

    def hash_sample_ids(self, salt: str) -> list:
        """Hash sample IDs with shared salt for PSI using scrypt."""
        salt_bytes = base64.b64decode(salt)
        return [
            base64.b64encode(
                hashlib.scrypt(str(sid).encode("utf-8"), salt=salt_bytes,
                               n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
            ).decode("utf-8")
            for sid in self._sample_ids
        ]

    def filter_to_common_samples(self, common_hashes: set, salt: str) -> None:
        """Keep only samples whose hashed ID is in the intersection."""
        salt_bytes = base64.b64decode(salt)
        keep = [
            i for i, sid in enumerate(self._sample_ids)
            if base64.b64encode(
                hashlib.scrypt(str(sid).encode("utf-8"), salt=salt_bytes,
                               n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
            ).decode("utf-8") in common_hashes
        ]
        self._sample_ids = [self._sample_ids[i] for i in keep]
        for v in self.variant_cols:
            self._dosage_std[v] = self._dosage_std[v][keep]
            self._dosage_raw[v] = self._dosage_raw[v][keep]

    def compute_partial_z(self, betas_geno_by_variant: dict) -> dict:
        """Partial linear predictor z_geno_v = dosage_std_v * beta_geno_v."""
        return {v: (self._dosage_std[v] * float(beta)).tolist()
                for v, beta in betas_geno_by_variant.items()}

    def geno_iterate(self, betas_geno_by_variant: dict,
                     residual_by_variant: dict, w_by_variant: dict) -> dict:
        """
        Compute gradient and (block-diagonal) Hessian for each variant's
        genotype beta, given residuals and weights from the clinical party.

        gradient_geno[v] = dosage_std.T @ residual       (scalar)
        h_gg[v]          = -(dosage_std.T * w) @ dosage  (scalar, negative)
        """
        gradient_geno_bv = {}
        h_gg_bv          = {}

        for v, beta in betas_geno_by_variant.items():
            dosage   = self._dosage_std[v]
            residual = np.array(residual_by_variant[v], dtype=np.float64)
            w        = np.array(w_by_variant[v],        dtype=np.float64)

            gradient_geno_bv[v] = float(dosage @ residual) - REGULARIZATION * float(beta)
            h_gg_bv[v]          = float(-(dosage * w) @ dosage) - REGULARIZATION

        return {
            'gradient_geno_by_variant': gradient_geno_bv,
            'h_gg_by_variant':          h_gg_bv,
        }

    def compute_maf_and_contingency(self, variant_ids: list,
                                    phenotype_vector: np.ndarray) -> dict:
        """MAF and 2×2 contingency table using raw (unstandardized) dosage."""
        results = {}
        for v in variant_ids:
            dosage   = self._dosage_raw[v]
            y        = phenotype_vector
            cases    = dosage[y == 1]
            controls = dosage[y == 0]

            results[v] = {
                'maf_cases':      float(cases.sum() / (2 * len(cases)))
                                  if len(cases) > 0 else float('nan'),
                'maf_controls':   float(controls.sum() / (2 * len(controls)))
                                  if len(controls) > 0 else float('nan'),
                'n_cases':        int(len(cases)),
                'n_controls':     int(len(controls)),
                'n_cases_ref':    int((2 * len(cases))    - cases.sum()),
                'n_cases_alt':    int(cases.sum()),
                'n_controls_ref': int((2 * len(controls)) - controls.sum()),
                'n_controls_alt': int(controls.sum()),
            }
        return results


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — NVFlare client entrypoint
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    data_dirs = [x for x in Path('/input/datasets/').iterdir() if x.resolve().is_dir()]
    data      = pd.read_csv(data_dirs[0] / 'dataset.csv')

    # Auto-detect party type from dataset schema
    has_phenotype = PHENOTYPE_COL in data.columns
    has_variants  = any(c.startswith('rs') for c in data.columns)

    if has_phenotype and not has_variants:
        party      = ClinicalParty(data)
        party_type = 'clinical'
    elif has_variants and not has_phenotype:
        party      = GenotypeParty(data)
        party_type = 'genotype'
    else:
        cols = list(data.columns)[:15]
        raise ValueError(
            f"Cannot determine party type from schema. "
            f"Expected either phenotype-only or genotype-only dataset. "
            f"Columns (first 15): {cols}"
        )

    flare.init()
    site_name = flare.get_site_name()

    while flare.is_running():
        inp  = flare.receive()
        task = inp.meta['current_task']

        # ── Identify party type to server ──────────────────────────────────
        if task == 'init':
            if party_type == 'clinical':
                flare.send(flare.FLModel(params={'party_type': 'clinical'}))
            else:
                flare.send(flare.FLModel(params={
                    'party_type':  'genotype',
                    'variant_cols': party.variant_cols,
                }))

        # ── PSI: hash sample IDs with server-provided salt ────────────────
        elif task == 'psi_hash':
            salt   = inp.params['salt']
            hashes = party.hash_sample_ids(salt)
            flare.send(flare.FLModel(params={'hashes': hashes}))

        # ── PSI: filter to common samples ─────────────────────────────────
        elif task == 'psi_filter':
            common_hashes = set(inp.params['common_hashes'])
            party.filter_to_common_samples(common_hashes, inp.params['salt'])
            flare.send(flare.FLModel(params={}))

        # ── Null model: clinical only ──────────────────────────────────────
        elif task == 'fit_null_model':
            if party_type == 'clinical':
                betas_null = party.fit_null_model()
                flare.send(flare.FLModel(params={
                    'betas_clin_null': betas_null.tolist()
                }))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Genotype → partial linear predictor ───────────────────────────
        elif task == 'partial_z':
            if party_type == 'genotype':
                partial_z = party.compute_partial_z(inp.params['betas_geno_by_variant'])
                flare.send(flare.FLModel(params={
                    'partial_z_geno_by_variant': partial_z
                }))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Clinical → gradients, Hessians, residuals, weights ────────────
        elif task == 'clinical_iterate':
            if party_type == 'clinical':
                out = party.clinical_iterate(
                    inp.params['betas_clin_by_variant'],
                    inp.params['partial_z_geno_by_variant'],
                )
                flare.send(flare.FLModel(params=out))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Genotype → gradient and Hessian from residuals ────────────────
        elif task == 'geno_iterate':
            if party_type == 'genotype':
                out = party.geno_iterate(
                    inp.params['betas_geno_by_variant'],
                    inp.params['residual_by_variant'],
                    inp.params['w_by_variant'],
                )
                flare.send(flare.FLModel(params=out))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Clinical sends phenotype vector for MAF computation ───────────
        elif task == 'get_phenotype':
            if party_type == 'clinical':
                flare.send(flare.FLModel(params={
                    'phenotype': party.y.tolist()
                }))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Genotype → MAF and contingency stats ──────────────────────────
        elif task == 'finalize_gwas':
            if party_type == 'genotype':
                y     = np.array(inp.params['phenotype_vector'], dtype=np.float64)
                stats = party.compute_maf_and_contingency(inp.params['variant_cols'], y)
                flare.send(flare.FLModel(params={'stats': stats}))
            else:
                flare.send(flare.FLModel(params={}))

        # ── Write results to output ────────────────────────────────────────
        elif task == 'write_output':
            results_df = pd.DataFrame(inp.params['results'])
            label      = party_type.capitalize()
            out_dir    = Path(f'/output/0/VFL GWAS Results ({label} Party)/')
            out_dir.mkdir(parents=True, exist_ok=True)
            results_df.to_csv(out_dir / 'dataset.csv', index=False)
            flare.send(flare.FLModel(params={}))
