"""
Total RWA Value (Stacked Area)
Four Pillars design theme
Data: rwa.xyz timeseries export
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import (
    create_figure, apply_style, save_chart,
    COLORS, SERIES_COLORS, setup_font, DPI,
)

OUTPUT_DIR = 'outputs/charts/rwa/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

df = pd.read_csv('outputs/data/rwa_total_value_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])

categories = [
    'US Treasury Debt', 'non-US Government Debt', 'Corporate Credit',
    'Stocks', 'Private Equity', 'Real Estate', 'Commodities',
    'Diversified Credit', 'Asset-Backed Credit', 'Active Strategies',
    'Specialty Finance', 'Venture Capital',
]

for col in categories:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / 1e9

# Group smaller categories
df['Other'] = (df['Stocks'] + df['Private Equity'] + df['Real Estate']
               + df['Diversified Credit'] + df['Active Strategies']
               + df['Specialty Finance'] + df['Venture Capital'])

# Filter from 2023
df = df[df['Date'] >= '2023-01-01'].copy()
df = df.set_index('Date').resample('W').last().reset_index()
df = df.dropna(subset=['US Treasury Debt'])

stack_cols = ['Other', 'Asset-Backed Credit', 'Corporate Credit',
              'non-US Government Debt', 'Commodities', 'US Treasury Debt']
stack_labels = ['Other', 'Asset-Backed Credit', 'Corporate Credit',
                'Non-US Govt Debt', 'Commodities', 'US Treasury Debt']
stack_colors = [
    '#6b7280',   # Other (neutral gray)
    '#f59e0b',   # Asset-Backed Credit (amber)
    '#e879f9',   # Corporate Credit (pink/fuchsia)
    '#a78bfa',   # Non-US Govt (purple)
    '#fbbf24',   # Commodities (gold)
    '#e4e4e7',   # US Treasury (light white/silver)
]

dates = df['Date']


def draw_rwa_stacked():
    setup_font()
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    stack_data = np.array([df[col].values for col in stack_cols])
    cumulative = np.cumsum(stack_data, axis=0)

    n = len(stack_cols)
    for i in range(n):
        bottom = cumulative[i - 1] if i > 0 else np.zeros(len(dates))
        top = cumulative[i]
        layer_alpha = 0.25 + 0.30 * (i / (n - 1))
        ax.fill_between(dates, bottom, top, color=stack_colors[i],
                        alpha=layer_alpha, linewidth=0, zorder=2)
        if i > 0:
            ax.plot(dates, bottom, color=stack_colors[i],
                    linewidth=0.4, alpha=0.3, zorder=3)

    total = cumulative[-1]
    ax.plot(dates, total, color=stack_colors[-1], linewidth=1.8, alpha=0.9, zorder=4)
    ax.plot(dates, total, color=stack_colors[-1], linewidth=4, alpha=0.15, zorder=3.5)

    # Y axis
    ax.set_ylim(0, 33)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))

    # X axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Grid & style
    ax.grid(True, axis='y', color=COLORS['grid'], alpha=0.5,
            linestyle=(0, (3.7, 1.6)), linewidth=1.0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
                   colors=COLORS['text_secondary'])
    ax.tick_params(axis='x', labelsize=12, pad=10,
                   colors=COLORS['text_secondary'])
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing rwa_total_value_stacked...')
    fig = draw_rwa_stacked()
    png, svg = save_chart(fig, 'rwa_total_value_stacked', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
