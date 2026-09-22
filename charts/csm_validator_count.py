"""
Lido CSM Validator Count
Area chart, Oct 2024 - Mar 2026
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
    setup_font, save_chart, apply_style, create_figure,
    COLORS, DPI, area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/lido/csm'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/csm_validator_count.csv')
df['Time'] = pd.to_datetime(df['Time'])
# Deduplicate: keep one row per day (latest)
df['date'] = df['Time'].dt.date
df = df.sort_values('Time').drop_duplicates(subset='date', keep='last')
df = df.sort_values('Time').reset_index(drop=True)

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    fig, ax = create_figure(chart_type='area')

    color = '#ee6666'  # Coral red (matching Dune original)
    dates = df['Time']
    values = df['Validators']

    # Area fill
    ax.fill_between(dates, values, alpha=0.25, color=color, zorder=2, step='post')
    ax.step(dates, values, where='post', color=color, linewidth=2, zorder=3)

    # Endpoint dot
    endpoint_dot(ax, dates.iloc[-1], values.iloc[-1], color=color, size=60)

    # Endpoint label
    ax.text(dates.iloc[-1], values.iloc[-1] + 600,
            f'{values.iloc[-1]:,.0f}',
            ha='center', va='bottom', fontsize=16, fontweight='bold',
            color=color, zorder=6)

    # ─── Y axis ─────────────────────────────────────────────────────
    ax.set_ylim(0, 20000)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 5000, 10000, 15000, 20000]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'{v/1000:.0f}k' if v > 0 else '0'))

    # ─── X axis ─────────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    apply_style(fig, ax, chart_type='area')

    return fig


if __name__ == '__main__':
    print('Drawing csm_validator_count...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'csm_validator_count', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
