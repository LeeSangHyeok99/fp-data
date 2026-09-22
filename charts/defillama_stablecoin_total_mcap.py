"""
Stablecoins - Total Market Cap (DefiLlama)
Four Pillars area chart, recreated from defillama.com/stablecoins reference image.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import (
    create_figure, save_chart,
    COLORS, setup_font, DPI,
    area_glow, endpoint_dot,
)

OUTPUT_DIR = 'outputs/charts/stablecoin/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

LINE_COLOR = '#3b8bff'

df = pd.read_csv('outputs/data/defillama_stablecoin_total_mcap.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Date'] >= '2018-01-01'].copy()
df['Mcap_B'] = df['TotalMcap_USD'] / 1e9
df = df.set_index('Date').resample('W').last().reset_index().dropna()


def draw():
    setup_font()
    fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    dates = df['Date']
    values = df['Mcap_B']

    area_glow(ax, dates, values, color=LINE_COLOR, n_layers=60, max_alpha=0.22, power=2.2)

    ax.plot(dates, values, color=LINE_COLOR, linewidth=2.0, alpha=0.95, zorder=4)
    ax.plot(dates, values, color=LINE_COLOR, linewidth=5, alpha=0.18, zorder=3.5)

    endpoint_dot(ax, dates.iloc[-1], values.iloc[-1], color=LINE_COLOR, size=60)

    ax.set_ylim(0, 350)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 100, 200, 300]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))

    ax.set_xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2026-06-01'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

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
    print('Drawing defillama_stablecoin_total_mcap...')
    fig = draw()
    png, svg = save_chart(fig, 'defillama_stablecoin_total_mcap', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
