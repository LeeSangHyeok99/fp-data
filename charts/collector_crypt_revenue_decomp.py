import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, gradient_rounded_bar

setup_font()

# =============================================================================
# Data (extracted from Blockworks Research chart, Apr 2024 - Jun 2026)
# =============================================================================
df = pd.read_csv('outputs/data/collector_crypt_revenue_decomp.csv')

CATS = df['category'].tolist()
VALS = df['value_musd'].tolist()
PCTS = df['pct_of_gross'].tolist()

# Semantic colors: gross (blue), buybacks/cost (red), net revenue (green)
BAR_COLORS = ['#5470c6', '#ee6666', '#91cc75']

OUTPUT_DIR = 'outputs/charts/collector_crypt/revenue'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    x = np.arange(len(CATS))
    width = 0.62

    # Gradient rounded bars
    for xi, v, c in zip(x, VALS, BAR_COLORS):
        gradient_rounded_bar(ax, x_center=xi, width=width, height=v, color=c)

    # Descending dashed arrow: Gross top -> pointing at the Net Revenue value
    ax.annotate('', xy=(x[2] - 0.30, VALS[2] + 72), xytext=(x[0], VALS[0]),
                arrowprops=dict(arrowstyle='-|>', linestyle=(0, (5, 4)),
                                color=COLORS['text_secondary'],
                                linewidth=1.3, alpha=0.7,
                                shrinkA=0, shrinkB=0, mutation_scale=16),
                zorder=4)

    # Value labels above bars
    for xi, v in zip(x, VALS):
        ax.text(xi, v + 18, f'${v:.1f}M', ha='center', va='bottom',
                fontsize=15, fontweight='bold', color='#ffffff', zorder=6)

    # "% of gross" annotations inside the larger bars
    ax.text(x[1], VALS[1] * 0.42, f'{PCTS[1]:.1f}%\nof gross',
            ha='center', va='center', fontsize=12.5, fontweight='bold',
            color='#ffffff', zorder=6)
    # Net revenue bar is too small -> float pct above it, matching the
    # "90.6% of gross" style and raised clear of the dashed connector
    ax.text(x[2], VALS[2] + 120, f'{PCTS[2]:.1f}%\nof gross',
            ha='center', va='center', fontsize=12.5, fontweight='bold',
            color='#ffffff', zorder=6)

    # Y axis: clean ticks, max 5, $M unit
    yticks = [0, 200, 400, 600]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'${t}M' for t in yticks],
                       fontsize=13, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(0, 680)

    # X axis labels
    ax.set_xticks(x)
    ax.set_xticklabels(CATS, fontsize=13, fontweight='bold',
                       color=COLORS['text'])
    ax.set_xlim(-0.7, len(CATS) - 0.3)

    # Grid + spines
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/collector_crypt_revenue_decomp_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 4.67), 'wide')
make_chart((6.95, 4.67), 'square')
print('Done: collector_crypt_revenue_decomp wide + square')
print(f'  Gross GMV ${VALS[0]}M | Buybacks ${VALS[1]}M ({PCTS[1]}%) | Net Rev ${VALS[2]}M ({PCTS[2]}%)')
