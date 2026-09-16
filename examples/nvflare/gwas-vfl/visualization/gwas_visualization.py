import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats

# ── I/O paths ─────────────────────────────────────────────────────────────────
GWAS_RESULTS_PATH     = "/input/0/dataset.csv"
VARIANT_METADATA_PATH = "/input/1/dataset.csv"
OUTPUT_DIR            = "/output/0"
FILE_DATA_DIR         = "/output/0/file_data"
MANHATTAN_FILENAME    = "manhattan_plot.png"
QQ_FILENAME           = "qq_plot.png"

# ── Config ────────────────────────────────────────────────────────────────────
GW_SIGNIFICANCE = 5e-8
SUGGESTIVE_LINE = 1e-5

os.makedirs(FILE_DATA_DIR, exist_ok=True)

# ── Load VFL GWAS results and merge with variant metadata ─────────────────────
results  = pd.read_csv(GWAS_RESULTS_PATH)
metadata = pd.read_csv(VARIANT_METADATA_PATH)[['variant_id', 'chromosome', 'position', 'gene']]
df       = results.merge(metadata, on='variant_id', how='left')
df       = df[df['p_value'].notna() & (df['p_value'] > 0)].copy()
df['neg_log10_p'] = -np.log10(df['p_value'])
df = df.sort_values(['chromosome', 'position']).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# MANHATTAN PLOT — coloured by gene
# ══════════════════════════════════════════════════════════════════════════════

def plot_manhattan(df):
    chromosomes = sorted(df['chromosome'].unique())

    chrom_offsets = {}
    offset = 0
    for chrom in chromosomes:
        chrom_offsets[chrom] = offset
        offset += df[df['chromosome'] == chrom]['position'].max() + 5_000_000

    df = df.copy()
    df['x_pos']      = df.apply(lambda r: r['position'] + chrom_offsets[r['chromosome']], axis=1)
    df['gene_label'] = df['gene'].fillna('intergenic')

    palette      = plt.cm.tab10.colors
    gene_colours = {
        gene: '#{:02x}{:02x}{:02x}'.format(
            int(palette[i % len(palette)][0] * 255),
            int(palette[i % len(palette)][1] * 255),
            int(palette[i % len(palette)][2] * 255),
        )
        for i, gene in enumerate(sorted(df['gene_label'].unique()))
    }

    fig, ax = plt.subplots(figsize=(16, 6))

    for gene, group in df.groupby('gene_label'):
        ax.scatter(group['x_pos'], group['neg_log10_p'],
                   color=gene_colours[gene], s=8, alpha=0.8, linewidths=0, label=gene)

    ax.axhline(-np.log10(GW_SIGNIFICANCE), color='red',    linestyle='--', linewidth=1.0)
    ax.axhline(-np.log10(SUGGESTIVE_LINE), color='orange', linestyle='--', linewidth=0.8)

    xlim = ax.get_xlim()
    ax.text(xlim[1], -np.log10(GW_SIGNIFICANCE),
            f' p={GW_SIGNIFICANCE:.0e}', va='center', fontsize=7, color='red')
    ax.text(xlim[1], -np.log10(SUGGESTIVE_LINE),
            f' p={SUGGESTIVE_LINE:.0e}', va='center', fontsize=7, color='orange')

    chrom_centres = {chrom: df[df['chromosome'] == chrom]['x_pos'].mean()
                     for chrom in chromosomes}
    ax.set_xticks(list(chrom_centres.values()))
    ax.set_xticklabels([str(c) for c in chrom_centres.keys()], fontsize=8)

    ax.set_xlabel('Chromosome', fontsize=12)
    ax.set_ylabel('-log₁₀(p-value)', fontsize=12)
    ax.set_title('Manhattan Plot — Vertical Federated GWAS (Schizophrenia)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=8, loc='upper left', markerscale=2, title='Gene', title_fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(FILE_DATA_DIR, MANHATTAN_FILENAME), dpi=150, bbox_inches='tight')
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# QQ PLOT
# ══════════════════════════════════════════════════════════════════════════════

def plot_qq(df):
    observed  = np.sort(df['neg_log10_p'].values)[::-1]
    n         = len(observed)
    expected  = -np.log10(np.arange(1, n + 1) / n)

    p_values_obs = 10 ** -observed
    chi2_obs     = scipy_stats.chi2.ppf(1 - p_values_obs, df=1)
    lambda_gc    = np.median(chi2_obs) / scipy_stats.chi2.ppf(0.5, df=1)

    fig, ax = plt.subplots(figsize=(7, 7))

    upper = -np.log10(np.array([max(1e-300, 1 - (0.05 / 2) ** (1 / k)) for k in range(n, 0, -1)]))
    lower = -np.log10(np.array([max(1e-300, (0.05 / 2) ** (1 / k))     for k in range(n, 0, -1)]))
    ax.fill_between(expected, lower, upper, alpha=0.15, color='grey', label='95% CI')

    ax.scatter(expected, observed, s=10, alpha=0.7, color='#762A83', linewidths=0)
    ax.plot([0, expected.max()], [0, expected.max()], 'r--', linewidth=1.0, label='Expected (null)')

    ax.set_xlabel('Expected -log₁₀(p-value)', fontsize=12)
    ax.set_ylabel('Observed -log₁₀(p-value)', fontsize=12)
    ax.set_title('QQ Plot — Vertical Federated GWAS (Schizophrenia)',
                 fontsize=14, fontweight='bold')
    ax.text(0.05, 0.92, f'λ = {lambda_gc:.3f}', transform=ax.transAxes,
            fontsize=11, color='black',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='grey'))
    ax.legend(fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(FILE_DATA_DIR, QQ_FILENAME), dpi=150, bbox_inches='tight')
    plt.close()


# ── Run all plots ─────────────────────────────────────────────────────────────
plot_manhattan(df)
plot_qq(df)

# ── Summary table with charts column ─────────────────────────────────────────
top10 = df.nsmallest(10, 'p_value')[
    ['variant_id', 'chromosome', 'position', 'gene',
     'p_value', 'p_fdr', 'OR', 'OR_lower_95', 'OR_upper_95',
     'MAF_cases', 'MAF_controls', 'gw_significant']
].reset_index(drop=True)

chart_files = [MANHATTAN_FILENAME, QQ_FILENAME]
charts      = chart_files + [np.nan] * (len(top10) - len(chart_files))
top10['charts'] = charts

top10.to_csv(os.path.join(OUTPUT_DIR, "dataset.csv"), index=False)
