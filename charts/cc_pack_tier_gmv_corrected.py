import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

setup_font()

# =============================================================================
# Scale-corrected Pack Tier GMV.
# Original monthly extraction was too high in absolute terms. We re-anchor each
# quarter's total to GMV = gacha flow / 1.906 (buyback = 90.6% of GMV), which
# lands Q1 2026 at ~$150M, matching Alea/Blockworks' reported $144.7M purchases.
# Monthly shape within a quarter, tier composition, and red% are preserved.
# =============================================================================
df = pd.read_csv('outputs/data/cc_pack_tier_gmv.csv')
df['date'] = pd.to_datetime(df['month'])

# quarter -> scale factor (target quarterly GMV / current extracted total)
QFACTOR = {
    '2025Q1': 1.053, '2025Q2': 0.869, '2025Q3': 0.677, '2025Q4': 0.590,
    '2026Q1': 0.782, '2026Q2': 0.828,
}
TIERS = ['p25', 'p50', 'p75', 'p80', 'p100', 'p250', 'p1000']


def qkey(d):
    return f'{d.year}Q{(d.month - 1) // 3 + 1}'


df['factor'] = df['date'].apply(lambda d: QFACTOR[qkey(d)])
for t in TIERS:
    df[t] = (df[t] * df['factor']).round(2)

# save corrected data
df[['month'] + TIERS + ['red_share_pct']].to_csv(
    'outputs/data/cc_pack_tier_gmv_corrected.csv', index=False)

TIER_COLORS = {
    'p25': '#cfd2d6', 'p50': '#aeb2b8', 'p75': '#8b9097', 'p80': '#6b727b',
    'p100': '#2e90d9', 'p250': '#ef9343', 'p1000': '#ee6666',
}

OUTPUT_DIR = 'outputs/charts/collector_crypt/gmv'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    x = np.arange(len(df))
    bottom = np.zeros(len(df))
    for tier in TIERS:
        vals = df[tier].values
        ax.bar(x, vals, 0.78, bottom=bottom, color=TIER_COLORS[tier],
               edgecolor='none', zorder=3)
        bottom += vals

    for xi, total, pct in zip(x, bottom, df['red_share_pct']):
        ax.text(xi, total + 2.0, f'{int(pct)}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color='#ee6666', zorder=6)

    yticks = [0, 25, 50, 75, 100]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'${t}M' for t in yticks], fontsize=12,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 118)

    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b %Y') for d in df['date']],
                       fontsize=10, fontweight='bold',
                       color=COLORS['text_secondary'], rotation=45, ha='right')
    ax.set_xlim(-0.7, len(df) - 0.3)

    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/cc_pack_tier_gmv_corrected_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((11.5, 5.2), 'wide')
totals = df[TIERS].sum(axis=1)
print('Done: cc_pack_tier_gmv_corrected')
print(f'  Cumulative ${totals.sum():.0f}M (was $776M) | May 2026 ${totals.iloc[-1]:.1f}M')
for q in QFACTOR:
    mask = df['date'].apply(qkey) == q
    print(f'  {q}: ${totals[mask].sum():.1f}M')
