"""
Circle (CRCL) Stock Price
Daily close, since IPO (Jun 2025)
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
    COLORS, DPI, area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/circle/token'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/crcl_price.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
df.set_index('Date', inplace=True)

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    color = '#5470c6'
    dates = df.index
    prices = df['Close']

    # Area glow
    area_glow(ax, dates, prices, color=color, max_alpha=0.20, power=2.0)

    # Line
    ax.plot(dates, prices, color=color, linewidth=2.5, zorder=4)

    # Endpoint dot + label
    endpoint_dot(ax, dates[-1], prices.iloc[-1], color=color, size=60)
    ax.text(dates[-1], prices.iloc[-1] + 8, f'${prices.iloc[-1]:.0f}',
            ha='center', va='bottom', fontsize=16, fontweight='bold',
            color=color, zorder=6)

    # ─── Axes ───────────────────────────────────────────────────────
    # Y axis
    ax.set_ylim(0, 275)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 50, 100, 150, 200, 250]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}'))

    # X axis
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    apply_style(fig, ax, chart_type='line')

    # Override tick sizes
    ax.tick_params(axis='y', labelsize=18)
    ax.tick_params(axis='x', labelsize=16)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    return fig


if __name__ == '__main__':
    print('Drawing crcl_price...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'crcl_price', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
