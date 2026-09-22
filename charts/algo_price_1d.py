"""
Algorand (ALGO) Daily Close Price
Source: TradingView / CoinMarketCap, 2025-06-27 ~ 2026-04-23
Marker: Google Quantum AI Paper Released (2026-03-30)
Four Pillars monochrome theme.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime
from pathlib import Path
from config import (
    setup_font, apply_style,
    DPI, area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/algorand/price'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

df = pd.read_csv('outputs/data/algo_price_1d.csv', parse_dates=['time'])
df.set_index('time', inplace=True)
df = df[df.index >= '2026-01-01']

EVENT_DATE = pd.Timestamp('2026-03-30')


def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    line_color = '#ffffff'
    surge_color = '#26a69a'

    dates = df.index
    prices = df['close']

    pre = df[df.index <= EVENT_DATE]
    post = df[df.index >= EVENT_DATE]

    area_glow(ax, pre.index, pre['close'], color=line_color, max_alpha=0.14, power=2.2)
    area_glow(ax, post.index, post['close'], color=surge_color, max_alpha=0.28, power=2.0)

    ax.plot(pre.index, pre['close'], color=line_color, linewidth=2.5, zorder=4)
    ax.plot(post.index, post['close'], color=surge_color, linewidth=2.8, zorder=5)

    ax.axvline(EVENT_DATE, color='#ffffff', linewidth=1.2,
               linestyle=(0, (4, 3)), alpha=0.85, zorder=3)

    ax.text(EVENT_DATE - pd.Timedelta(days=2), 0.155,
            'Google Quantum AI Paper Released',
            ha='right', va='top', fontsize=14, fontweight='bold',
            color='#ffffff', zorder=6)
    ax.text(EVENT_DATE - pd.Timedelta(days=2), 0.148,
            '2026-03-30',
            ha='right', va='top', fontsize=12, fontweight='bold',
            color='#787b86', zorder=6)

    peak_row = post.loc[post['close'].idxmax()]
    peak_date, peak_price = peak_row.name, peak_row['close']
    surge_pct = (peak_price / pre['close'].min() - 1) * 100

    endpoint_dot(ax, peak_date, peak_price, color=surge_color, size=70)
    ax.text(peak_date + pd.Timedelta(days=3), peak_price + 0.012,
            f'${peak_price:.3f}\n+{surge_pct:.0f}% from low',
            ha='left', va='bottom', fontsize=13, fontweight='bold',
            color=surge_color, zorder=6)

    last_price = prices.iloc[-1]
    endpoint_dot(ax, dates[-1], last_price, color=surge_color, size=55)
    ax.text(dates[-1] + pd.Timedelta(days=3), last_price - 0.005,
            f'${last_price:.3f}',
            ha='left', va='top', fontsize=12, fontweight='bold',
            color=surge_color, zorder=6)

    ax.set_ylim(0.06, 0.16)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0.06, 0.08, 0.10, 0.12, 0.14, 0.16]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.2f}'))

    ax.xaxis.set_major_locator(mticker.FixedLocator([
        mdates.date2num(pd.Timestamp('2026-01-01')),
        mdates.date2num(pd.Timestamp('2026-02-01')),
        mdates.date2num(pd.Timestamp('2026-03-01')),
        mdates.date2num(pd.Timestamp('2026-04-01')),
    ]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    ax.set_xlim(dates[0] - pd.Timedelta(days=2),
                pd.Timestamp('2026-04-30'))

    apply_style(fig, ax, chart_type='line')

    ax.tick_params(axis='y', labelsize=18)
    ax.tick_params(axis='x', labelsize=16)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    return fig


if __name__ == '__main__':
    print('Drawing algo_price_1d...')
    fig = draw_chart()
    png_path = f'{OUTPUT_DIR}/algo_price_1d.png'
    svg_path = f'{OUTPUT_DIR}/algo_price_1d.svg'
    fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
                bbox_inches='tight', transparent=True)
    fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
                bbox_inches='tight', transparent=True)
    print(f'  → {png_path}')
    plt.close(fig)
    print('Done.')
