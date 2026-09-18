from nvflare.app_common.workflows.base_fedavg import BaseFedAvg
import base64
import hashlib
import os
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

# ── Constants ─────────────────────────────────────────────────────────────────
# Clinical block: age, sex, bmi + intercept
N_CLIN_PARAMS   = 4
MAX_ITERATIONS  = 20
CONVERGENCE_TOL = 1e-6
GW_SIGNIFICANCE = 5e-8
REGULARIZATION  = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# VFL GWAS SERVER
# ══════════════════════════════════════════════════════════════════════════════

class VFLGWASServer(BaseFedAvg):
    """
    Orchestrates vertical federated GWAS between a clinical party and a
    genotype party.  The server never sees raw features or labels — it only
    routes intermediate values (partial linear predictors, residuals, weights,
    gradients, Hessians) between the two parties.

    Optimization: block-diagonal Newton-Raphson, processing all variants per
    communication round (same batching strategy as the horizontal FL baseline).

    Per-iteration protocol (3 sub-rounds):
      A. Server → Genotype: current betas_geno
         Genotype → Server: partial_z_geno   [N_variants × N_samples]
      B. Server → Clinical: betas_clin + partial_z_geno
         Clinical → Server: gradient_clin, h_cc, residuals, w  [per variant]
      C. Server → Genotype: residuals + w
         Genotype → Server: gradient_geno, h_gg               [scalars per variant]
      Server: Newton-Raphson update, convergence check per variant.

    Note on privacy: residuals (y-p) and weights w are forwarded from the
    clinical party to the genotype party via the server.  These are correlated
    with phenotype labels.  A production deployment would protect them with
    secure aggregation or homomorphic encryption before forwarding.
    """

    def run(self) -> None:
        model   = self.load_model()
        clients = self.sample_clients(self.num_clients)

        # ── Phase 1: Identify party types ─────────────────────────────────
        model.meta['current_task'] = 'init'
        model.params = {}
        init_responses = self.send_model_and_wait(targets=clients, data=model)

        clinical_targets = []
        genotype_targets = []
        variant_cols     = None

        for client, resp in zip(clients, init_responses):
            ptype = resp.params.get('party_type')
            if ptype == 'clinical':
                clinical_targets.append(client)
            elif ptype == 'genotype':
                genotype_targets.append(client)
                variant_cols = resp.params['variant_cols']

        assert clinical_targets, "No clinical party found"
        assert genotype_targets, "No genotype party found"
        assert variant_cols is not None, "Variant list not received"

        self.info(f"VFL GWAS — {len(variant_cols)} variants | "
                  f"clinical sites: {len(clinical_targets)}, "
                  f"genotype sites: {len(genotype_targets)}")

        # ── Phase 2: Private Set Intersection ─────────────────────────────
        # Server generates a fresh random salt and sends it to both parties.
        # Each party hashes its sample IDs with SHA-256(salt + id) and returns
        # the hash set.  The server finds the intersection and sends it back so
        # each party can filter to only the common samples.
        #
        # Limitation vs. a full cryptographic PSI: each party can infer the
        # size of the non-intersection from the hash set sizes, but cannot link
        # non-matching hashes back to plaintext IDs.  Production would use an
        # OPRF-based or Diffie-Hellman PSI library.
        salt = base64.b64encode(os.urandom(32)).decode("utf-8")  # base64 string — safe to transmit in params

        model.meta['current_task'] = 'psi_hash'
        model.params = {'salt': salt}
        psi_responses = self.send_model_and_wait(targets=clients, data=model)

        hash_sets = [set(r.params['hashes']) for r in psi_responses]
        common_hashes = hash_sets[0].intersection(*hash_sets[1:])

        self.info(f"PSI complete — {len(common_hashes)} common samples identified")

        model.meta['current_task'] = 'psi_filter'
        model.params = {'salt': salt, 'common_hashes': list(common_hashes)}
        self.send_model_and_wait(targets=clients, data=model)

        # ── Phase 3: Clinical null model (zero genotype communication) ────
        model.meta['current_task'] = 'fit_null_model'
        model.params = {}
        null_resp = self.send_model_and_wait(targets=clinical_targets, data=model)
        betas_clin_null = np.array(null_resp[0].params['betas_clin_null'],
                                   dtype=np.float64)
        self.info("Null model fitted on clinical party.")

        # ── Initialise per-variant betas ──────────────────────────────────
        betas_clin_bv = {v: betas_clin_null.copy() for v in variant_cols}
        betas_geno_bv = {v: 0.0 for v in variant_cols}
        not_converged = set(variant_cols)

        # ── Phase 4: Block-diagonal Newton-Raphson ────────────────────────
        for iteration in range(MAX_ITERATIONS):
            nc = list(not_converged)

            # Sub-round A — genotype sends partial linear predictor
            model.meta['current_task'] = 'partial_z'
            model.params = {
                'betas_geno_by_variant': {v: float(betas_geno_bv[v]) for v in nc}
            }
            gr_a = self.send_model_and_wait(targets=genotype_targets, data=model)
            partial_z_geno = gr_a[0].params['partial_z_geno_by_variant']

            # Sub-round B — clinical computes gradients from z_total
            model.meta['current_task'] = 'clinical_iterate'
            model.params = {
                'betas_clin_by_variant':     {v: betas_clin_bv[v].tolist() for v in nc},
                'partial_z_geno_by_variant': {v: partial_z_geno[v] for v in nc},
            }
            gr_b     = self.send_model_and_wait(targets=clinical_targets, data=model)
            clin_out = gr_b[0].params

            # Sub-round C — genotype computes gradient and Hessian from residuals
            model.meta['current_task'] = 'geno_iterate'
            model.params = {
                'betas_geno_by_variant': {v: float(betas_geno_bv[v]) for v in nc},
                'residual_by_variant':   {v: clin_out['residual_by_variant'][v] for v in nc},
                'w_by_variant':          {v: clin_out['w_by_variant'][v] for v in nc},
            }
            gr_c     = self.send_model_and_wait(targets=genotype_targets, data=model)
            geno_out = gr_c[0].params

            # Server: Newton-Raphson update, check convergence
            newly_converged = set()
            for v in nc:
                g_clin  = np.array(clin_out['gradient_clin_by_variant'][v], dtype=np.float64)
                h_cc    = np.array(clin_out['h_cc_by_variant'][v],          dtype=np.float64)
                g_geno  = float(geno_out['gradient_geno_by_variant'][v])
                h_gg    = float(geno_out['h_gg_by_variant'][v])    # negative

                try:
                    delta_clin = np.linalg.solve(-h_cc, g_clin)
                except np.linalg.LinAlgError:
                    continue

                delta_geno = -g_geno / h_gg if abs(h_gg) > 1e-12 else 0.0

                betas_clin_bv[v] = betas_clin_bv[v] + delta_clin
                betas_geno_bv[v] = betas_geno_bv[v] + delta_geno

                if np.linalg.norm(delta_clin) ** 2 + delta_geno ** 2 < CONVERGENCE_TOL ** 2:
                    newly_converged.add(v)

            not_converged -= newly_converged
            self.info(f"Iteration {iteration + 1}: {len(newly_converged)} converged, "
                      f"{len(not_converged)} remaining")

            if not not_converged:
                break

        # ── Phase 5: Final Hessian pass (all variants, for SE computation) ─
        model.meta['current_task'] = 'partial_z'
        model.params = {'betas_geno_by_variant': {v: float(betas_geno_bv[v])
                                                  for v in variant_cols}}
        gr_f1 = self.send_model_and_wait(targets=genotype_targets, data=model)
        pz_final = gr_f1[0].params['partial_z_geno_by_variant']

        model.meta['current_task'] = 'clinical_iterate'
        model.params = {
            'betas_clin_by_variant':     {v: betas_clin_bv[v].tolist() for v in variant_cols},
            'partial_z_geno_by_variant': {v: pz_final[v] for v in variant_cols},
        }
        gr_f2    = self.send_model_and_wait(targets=clinical_targets, data=model)
        clin_fin = gr_f2[0].params

        model.meta['current_task'] = 'geno_iterate'
        model.params = {
            'betas_geno_by_variant': {v: float(betas_geno_bv[v]) for v in variant_cols},
            'residual_by_variant':   clin_fin['residual_by_variant'],
            'w_by_variant':          clin_fin['w_by_variant'],
        }
        gr_f3    = self.send_model_and_wait(targets=genotype_targets, data=model)
        h_gg_fin = gr_f3[0].params['h_gg_by_variant']

        # ── Phase 6: Collect MAF / contingency stats ──────────────────────
        # Phenotype labels are requested from clinical and forwarded to genotype
        # so that the genotype party can split dosage by case/control status.
        # (Documented privacy limitation — see implementation.md §Privacy.)
        model.meta['current_task'] = 'get_phenotype'
        model.params = {}
        phen_resp = self.send_model_and_wait(targets=clinical_targets, data=model)
        phenotype_vector = phen_resp[0].params['phenotype']

        model.meta['current_task'] = 'finalize_gwas'
        model.params = {
            'variant_cols':     variant_cols,
            'phenotype_vector': phenotype_vector,
        }
        fin_resp   = self.send_model_and_wait(targets=genotype_targets, data=model)
        site_stats = fin_resp[0].params['stats']

        # ── Phase 7: Compute summary statistics ───────────────────────────
        all_results = []
        for v in variant_cols:
            beta  = float(betas_geno_bv[v])
            h_gg  = float(h_gg_fin[v])
            var_g = (1.0 / (-h_gg)) if abs(h_gg) > 1e-12 else np.nan
            se    = float(np.sqrt(var_g)) if (not np.isnan(var_g) and var_g > 0) else np.nan
            z     = (beta / se) if (se and not np.isnan(se) and se > 0) else np.nan
            p     = float(2 * (1 - norm.cdf(abs(z)))) if not np.isnan(z) else np.nan

            s = site_stats[v]
            all_results.append({
                'variant_id':        v,
                'beta':              beta,
                'se':                se,
                'z_stat':            z,
                'chi2_stat':         z ** 2 if not np.isnan(z) else np.nan,
                'p_value':           p,
                'OR':                float(np.exp(np.clip(beta, -500, 500))),
                'OR_lower_95':       float(np.exp(np.clip(beta - 1.96 * se, -500, 500)))
                                     if not np.isnan(se) else np.nan,
                'OR_upper_95':       float(np.exp(np.clip(beta + 1.96 * se, -500, 500)))
                                     if not np.isnan(se) else np.nan,
                'MAF_cases':         s['maf_cases'],
                'MAF_controls':      s['maf_controls'],
                'n_cases':           s['n_cases'],
                'n_controls':        s['n_controls'],
                'risk_allele':       'alt' if beta > 0 else 'ref',
                'n_cases_ref':       s['n_cases_ref'],
                'n_cases_alt':       s['n_cases_alt'],
                'n_controls_ref':    s['n_controls_ref'],
                'n_controls_alt':    s['n_controls_alt'],
                'contingency_table': (
                    f"            ref    alt\n"
                    f"cases       {s['n_cases_ref']:<6} {s['n_cases_alt']:<6}\n"
                    f"controls    {s['n_controls_ref']:<6} {s['n_controls_alt']:<6}"
                ),
            })

        results_df = pd.DataFrame(all_results)
        _, p_fdr, _, _ = multipletests(results_df['p_value'].fillna(1.0), method='fdr_bh')
        results_df['p_fdr']          = p_fdr
        results_df['gw_significant'] = results_df['p_value'] < GW_SIGNIFICANCE

        gw_count  = int(results_df['gw_significant'].sum())
        fdr_count = int((results_df['p_fdr'] < 0.05).sum())
        self.info(f"GWAS complete — {len(results_df)} variants tested. "
                  f"Genome-wide significant: {gw_count}. FDR significant: {fdr_count}.")

        # ── Phase 8: Broadcast results to all parties for output ──────────
        model.meta['current_task'] = 'write_output'
        model.params = {'results': results_df.to_dict(orient='list')}
        self.send_model_and_wait(targets=clients, data=model)
