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
# Data (extracted from reference image: Collector Crypt pack tier GMV mix)
# Gray tiers ($25-$80) are visual estimates; $250/$1000 split derived from the
# red% label (= ($250+$1000) share of total GMV) and bar heights.
# =============================================================================
df = pd.read_csv('outputs/data/cc_pack_tier_gmv.csv')
df['date'] = pd.to_datetime(df['month'])

TIERS = ['p25', 'p50', 'p75', 'p80', 'p100', 'p250', 'p1000']
TIER_COLORS = {
    'p25':   '#cfd2d6',  # lightest gray
    'p50':   '#aeb2b8',
    'p75':   '#8b9097',
    'p80':   '#6b727b',  # darkest gray
    'p100':  '#2e90d9',  # bright azure blue
    'p250':  '#ef9343',  # orange
    'p1000': '#ee6666',  # red
}

OUTPUT_DIR = 'outputs/charts/collector_crypt/gmv'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    x = np.arange(len(df))
    width = 0.78
    bottom = np.zeros(len(df))

    for tier in TIERS:
        vals = df[tier].values
        ax.bar(x, vals, width, bottom=bottom, color=TIER_COLORS[tier],
               edgecolor='none', zorder=3)
        bottom += vals

    # red% labels above each bar (= $250+$1000 share of total GMV)
    for xi, total, pct in zip(x, bottom, df['red_share_pct']):
        ax.text(xi, total + 2.5, f'{int(pct)}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color='#ee6666', zorder=6)

    # y axis: clean ticks, $M
    yticks = [0, 40, 80, 120]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'${t}M' for t in yticks], fontsize=12,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 142)

    # x axis: month labels (Mon YYYY)
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b %Y') for d in df['date']],
                       fontsize=10, fontweight='bold',
                       color=COLORS['text_secondary'], rotation=45, ha='right')
    ax.set_xlim(-0.7, len(df) - 0.3)

    # grid + spines
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/cc_pack_tier_gmv_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((11.5, 5.2), 'wide')
totals = df[TIERS].sum(axis=1)
print('Done: cc_pack_tier_gmv')
print(f'  Months {len(df)} | Latest total ${totals.iloc[-1]:.1f}M'
      f' | Peak ${totals.max():.1f}M')
