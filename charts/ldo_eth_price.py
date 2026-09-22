"""
LDO/ETH Price Chart
Weekly, Jan 2021 - Mar 2026
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

OUTPUT_DIR = 'outputs/charts/lido/token'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv(
    '/Users/ijaheun/Downloads/LDO_All_graph_coinmarketcap.csv',
    sep=';',
    parse_dates=['timestamp'],
)
df.set_index('timestamp', inplace=True)

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    color = '#00A3FF'  # Lido brand blue
    dates = df.index
    values = df['price']

    # Area glow
    area_glow(ax, dates, values, color=color, max_alpha=0.25, power=1.8)

    # Line
    ax.plot(dates, values, color=color, linewidth=2, zorder=4)

    # Endpoint dot
    endpoint_dot(ax, dates[-1], values.iloc[-1], color=color, size=60)

    # ─── Axes ───────────────────────────────────────────────────────
    # Y axis
    ax.set_ylim(0, 0.0020)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 0.0005, 0.0010, 0.0015, 0.0020]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'{v:.4f}'
    ))

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
    print('Drawing ldo_eth_price...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'ldo_eth_price', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
