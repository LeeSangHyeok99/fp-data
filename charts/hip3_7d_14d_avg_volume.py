"""
HIP-3 7-day and 14-day Average Daily Volume
Dual line chart — HRC theme + Hyperliquid brand colors
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

# ─── Hyperliquid brand colors ──────────────────────────────────────────
COLOR_7D = '#50e3c2'    # Hyperliquid teal
COLOR_14D = '#7c3aed'   # Electric purple

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_7d_14d_avg_volume.csv')
df.columns = ['date', '7d_avg_volume', '14d_avg_volume', '7d_share', '14d_share']
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df['7d_avg_volume'] = pd.to_numeric(df['7d_avg_volume'], errors='coerce')
df['14d_avg_volume'] = pd.to_numeric(df['14d_avg_volume'], errors='coerce')
df['7d_B'] = df['7d_avg_volume'] / 1e9
df['14d_B'] = df['14d_avg_volume'] / 1e9


# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # ─── Lines ─────────────────────────────────────────────────────
    mask_7d = df['7d_B'].notna()
    mask_14d = df['14d_B'].notna()

    ax.plot(df.loc[mask_7d, 'date'], df.loc[mask_7d, '7d_B'],
            color=COLOR_7D, linewidth=2.5, zorder=5, alpha=0.9)
    ax.plot(df.loc[mask_14d, 'date'], df.loc[mask_14d, '14d_B'],
            color=COLOR_14D, linewidth=2.5, zorder=4, alpha=0.9)

    # ─── Area glow ────────────────────────────────────────────────
    ax.fill_between(df.loc[mask_7d, 'date'], 0, df.loc[mask_7d, '7d_B'],
                    color=COLOR_7D, alpha=0.08, zorder=2)
    ax.fill_between(df.loc[mask_14d, 'date'], 0, df.loc[mask_14d, '14d_B'],
                    color=COLOR_14D, alpha=0.08, zorder=2)

    # ─── Endpoint dots ────────────────────────────────────────────
    last_7d = df.loc[mask_7d].iloc[-1]
    last_14d = df.loc[mask_14d].iloc[-1]
    ax.scatter(last_7d['date'], last_7d['7d_B'], color=COLOR_7D,
               s=60, zorder=6, edgecolors='white', linewidth=1.5)
    ax.scatter(last_14d['date'], last_14d['14d_B'], color=COLOR_14D,
               s=60, zorder=6, edgecolors='white', linewidth=1.5)

    # ─── $2B reference line ───────────────────────────────────────
    ax.axhline(y=2.0, color='#ffffff', linewidth=1.0, linestyle='--',
               alpha=0.4, zorder=3)

    # ─── Y axis ───────────────────────────────────────────────────
    ax.set_ylim(0, 3.0)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'${v:.1f}B' if v > 0 else '$0B'))
    ax.tick_params(axis='y', labelsize=18, pad=15, length=0,
                   colors=COLORS['text_secondary'])

    # ─── X axis ───────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right', fontweight='bold')

    # ─── Grid ─────────────────────────────────────────────────────
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing hip3_7d_14d_avg_volume (HRC)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_7d_14d_avg_volume', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
