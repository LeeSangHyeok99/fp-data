"""
Stablecoin Market Cap Growth (Stacked Area)
+ TradFi acquisition annotation markers
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
    COLORS, setup_font, DPI, DEFAULT_FIGSIZE,
    area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/stablecoin/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Load data
df = pd.read_csv('outputs/data/stablecoin_market_cap_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Top stablecoins to show individually
top_coins = ['Tether USDt', 'USDC', 'USDS', 'Ethena USDe', 'Dai Stablecoin', 'Paypal USD']
other_cols = [c for c in df.columns if c not in ['Timestamp', 'Date', 'Measure'] + top_coins]

# Fill NaN with 0 and convert to $B
for col in top_coins + other_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / 1e9

df['Others'] = df[other_cols].sum(axis=1)

# Filter from 2020 onward for cleaner view
df = df[df['Date'] >= '2020-01-01'].copy()

# Resample weekly for smoother chart
df = df.set_index('Date').resample('W').last().reset_index()
df = df.dropna(subset=['Tether USDt'])

# Stack order (bottom to top): Others, PYUSD, Dai, Ethena, USDS, USDC, Tether
stack_cols = ['Others', 'Paypal USD', 'Dai Stablecoin', 'Ethena USDe', 'USDS', 'USDC', 'Tether USDt']
stack_colors = [
    '#4a4a4a',   # Others gray
    '#0070e0',   # PayPal blue
    '#f5ac37',   # Dai orange
    '#333333',   # Ethena dark
    '#6c63ff',   # Sky/USDS purple
    '#2775ca',   # USDC blue
    '#26a17b',   # Tether green
]

dates = df['Date']


def draw_stacked_area():
    setup_font()
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Build stacked data
    stack_data = np.array([df[col].values for col in stack_cols])
    cumulative = np.cumsum(stack_data, axis=0)

    # Fill areas with gradient alpha (lower layers more transparent)
    n = len(stack_cols)
    for i in range(n):
        bottom = cumulative[i - 1] if i > 0 else np.zeros(len(dates))
        top = cumulative[i]
        # Top layers more opaque, bottom layers softer
        layer_alpha = 0.35 + 0.35 * (i / (n - 1))
        ax.fill_between(dates, bottom, top, color=stack_colors[i], alpha=layer_alpha, linewidth=0, zorder=2)
        # Subtle edge line
        if i > 0:
            ax.plot(dates, bottom, color=stack_colors[i], linewidth=0.4, alpha=0.3, zorder=3)

    # Top line with slight glow
    total = cumulative[-1]
    ax.plot(dates, total, color=stack_colors[-1], linewidth=1.8, alpha=0.9, zorder=4)
    ax.plot(dates, total, color=stack_colors[-1], linewidth=4, alpha=0.15, zorder=3.5)

    # TradFi event annotations (white dashed lines + labels)
    events = [
        ('2025-02-20', 'Stripe\nBridge $1.1B'),
        ('2026-03-17', 'Mastercard\nBVNK $1.8B'),
    ]
    for date_str, label in events:
        event_date = pd.Timestamp(date_str)
        if event_date >= dates.iloc[0]:
            ax.axvline(x=event_date, color='#e4e4e7', linestyle='--', linewidth=0.8, alpha=0.5, zorder=5)
            ax.text(event_date, total.max() * 1.02, label, fontsize=8, fontweight='bold',
                    color='#e4e4e7', alpha=0.8, ha='center', va='bottom', clip_on=False,
                    linespacing=1.3)

    # Y axis
    ax.set_ylim(0, 350)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 100, 200, 300]))
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

    ax.tick_params(axis='y', labelsize=14, pad=15, length=0, colors=COLORS['text_secondary'])
    ax.tick_params(axis='x', labelsize=12, pad=10, colors=COLORS['text_secondary'])
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing stablecoin_market_growth_stacked...')
    fig = draw_stacked_area()
    png, svg = save_chart(fig, 'stablecoin_market_growth_stacked', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
