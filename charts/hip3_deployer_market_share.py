"""
HIP-3 Deployer Market Share (100% Stacked Area)
HRC theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/hrc')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import (
    setup_font, save_chart, COLORS, DPI, GRID_CONFIG,
)

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Deployer colors (consistent with OI market share chart) ──────────
DEPLOYER_COLORS = {
    'xyz':  '#7EC8B4',   # Soft sage teal
    'cash': '#5B93B5',   # Steel blue
    'hyna': '#9583B8',   # Muted lavender
    'km':   '#C9A870',   # Warm sand
    'flx':  '#6BAAB5',   # Dusty teal
    'vntl': '#B87D8A',   # Dusty rose
}

# Stack order: XYZ at bottom (largest), then descending by latest share
SERIES = ['xyz', 'cash', 'hyna', 'km', 'flx', 'vntl']
LABELS = ['Trade.xyz', 'Cash (Dreamcash)', 'HyENA', 'Markets by Kinetiq', 'Felix', 'Ventuals']

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_deployer_market_share.csv', parse_dates=['date'])

# Parse percentage strings to float
for col in [f'{s}_share' for s in SERIES]:
    df[col] = df[col].str.replace('%', '').astype(float)


# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    dates = df['date']
    values = [df[f'{s}_share'].values for s in SERIES]
    colors = [DEPLOYER_COLORS[s] for s in SERIES]

    ax.stackplot(dates, *values, colors=colors, alpha=0.85, zorder=3)

    # ─── Y axis ───────────────────────────────────────────────────
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 20, 40, 60, 80, 100]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax.tick_params(axis='y', labelsize=18, pad=15, length=0,
                   colors=COLORS['text_secondary'])

    # ─── X axis ───────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=0)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='center', fontweight='bold')

    # ─── Grid ─────────────────────────────────────────────────────
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing hip3_deployer_market_share (HRC)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_deployer_market_share', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
