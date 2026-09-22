"""
DEX to CEX Spot Volume Ratio
Monthly line chart, Jan 2021 - Nov 2025
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
    COLORS, DPI, SERIES_COLORS, area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/dex/volume'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/dex_cex_ratio.csv', parse_dates=['date'])
df.set_index('date', inplace=True)

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    color = '#9a60b4'  # purple
    dates = df.index
    values = df['ratio']

    # Area glow
    area_glow(ax, dates, values, color=color, max_alpha=0.22, power=2.0)

    # Line
    ax.plot(dates, values, color=color, linewidth=2.5, zorder=4)

    # Endpoint dot
    endpoint_dot(ax, dates[-1], values.iloc[-1], color=color, size=60)

    # Annotations removed per user request

    # ─── Axes ───────────────────────────────────────────────────────
    # Y axis
    ax.set_ylim(0, 50)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30, 40, 50]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))

    # X axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    apply_style(fig, ax, chart_type='line')

    # Override tick sizes
    ax.tick_params(axis='y', labelsize=22)
    ax.tick_params(axis='x', labelsize=20)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    return fig


if __name__ == '__main__':
    print('Drawing dex_cex_ratio...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'dex_cex_ratio', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
