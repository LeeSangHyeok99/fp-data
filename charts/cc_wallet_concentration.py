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
# Data (extracted from reference image: CC native API wallet concentration)
# 645 pulls, 43 wallets, 47 minutes
# =============================================================================
df = pd.read_csv('outputs/data/cc_wallet_concentration.csv')

# Semantic group colors: top5 (red), top6-10 (orange), top11-20 (blue), rest (gray)
GROUP_COLORS = {
    'top5': '#ee6666',
    'top6_10': '#fc8452',
    'top11_20': '#5470c6',
    'rest': '#787b86',
}

LABELS = df['rank'].apply(lambda r: f'#{r}').tolist()
LABELS[-1] = df['wallet'].iloc[-1]  # last row already carries its own label
# build y tick labels: rank only, no parenthetical wallet id
ROW_LABELS = []
for _, row in df.iterrows():
    if row['group'] == 'rest':
        ROW_LABELS.append('#21-43')
    else:
        ROW_LABELS.append(f"#{row['rank']}")

VALS = df['pulls'].tolist()
PCTS = df['pct'].tolist()
COLS = [GROUP_COLORS[g] for g in df['group']]

OUTPUT_DIR = 'outputs/charts/collector_crypt/concentration'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    n = len(VALS)
    # top row first -> invert y so rank #1 sits at the top
    y = np.arange(n)[::-1]

    ax.barh(y, VALS, color=COLS, height=0.72, zorder=3,
            edgecolor='none')

    # value + pct labels at bar ends
    for yi, v, p in zip(y, VALS, PCTS):
        ax.text(v + 1.5, yi, f'{v} ({p:.1f}%)', ha='left', va='center',
                fontsize=9.5, fontweight='bold', color=COLORS['text'],
                zorder=5)

    # y tick labels = wallet ids
    ax.set_yticks(y)
    ax.set_yticklabels(ROW_LABELS, fontsize=9.5, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(-0.7, n - 0.3)

    # x axis: clean ticks (5 max, multiples of 25)
    xticks = [0, 25, 50, 75, 100]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(t) for t in xticks], fontsize=10.5,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_xlim(0, 122)

    # grid on x, spines off
    ax.grid(True, axis='x', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/cc_wallet_concentration_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.7), 'wide')
print('Done: cc_wallet_concentration')
print(f'  Total {sum(VALS)} pulls | Top5 {sum(VALS[:5])} ({sum(PCTS[:5]):.1f}%)'
      f' | Top10 {sum(VALS[:10])} ({sum(PCTS[:10]):.1f}%)'
      f' | Top20 {sum(VALS[:20])} ({sum(PCTS[:20]):.1f}%)')
