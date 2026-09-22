"""
HIP-3 CL-USDC Daily Volume
Jan 6 - Mar 25, 2026 bar chart
Four Pillars theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    setup_font, save_chart, apply_style,
    COLORS, DPI,
)

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_cl_usdc_daily_volume.csv', parse_dates=['date'])
df.set_index('date', inplace=True)

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    color = '#5470c6'  # blue
    dates = df.index
    values = df['daily_volume']  # ASXN API single-side volume

    # Bar chart
    ax.bar(dates, values, width=0.8, color=color, alpha=0.85, zorder=3)

    # ─── Axes ───────────────────────────────────────────────────────
    # Y axis — max ~$1.87B single-side, use $0B to $2B with $500M steps
    ax.set_ylim(0, 2e9)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 0.5e9, 1e9, 1.5e9, 2e9]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'${v/1e9:.1f}B'
    ))

    # X axis — full range with biweekly ticks
    ax.set_xlim(
        dates[0] - pd.Timedelta(days=1),
        dates[-1] + pd.Timedelta(days=1),
    )
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    apply_style(fig, ax, chart_type='bar')

    # Override tick sizes
    ax.tick_params(axis='y', labelsize=22)
    ax.tick_params(axis='x', labelsize=20)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    return fig


if __name__ == '__main__':
    print('Drawing hip3_cl_usdc_daily_volume...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_cl_usdc_daily_volume', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
