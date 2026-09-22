"""
Single-Name Equity Cumulative Volume by Ticker
Horizontal bar, US vs Korean equities color split
HRC theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/hrc')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    setup_font, save_chart, COLORS, DPI, GRID_CONFIG,
)

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

COLOR_US = '#2d8c6f'
COLOR_KR = '#f59e0b'

df = pd.read_csv('outputs/data/single_name_equity_volume_q1_2026.csv')
df = df.sort_values('volume_musd', ascending=True).reset_index(drop=True)


def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    colors = [COLOR_US if r == 'US' else COLOR_KR for r in df['region']]
    bars = ax.barh(
        df['ticker'],
        df['volume_musd'],
        color=colors,
        height=0.7,
        zorder=3,
    )

    for bar, value in zip(bars, df['volume_musd']):
        ax.text(
            bar.get_width() + 15,
            bar.get_y() + bar.get_height() / 2,
            f'${value:,.0f}M',
            va='center',
            ha='left',
            fontsize=14,
            fontweight='bold',
            color=COLORS['text'],
        )

    ax.set_xlim(0, 1400)
    ax.xaxis.set_major_locator(mticker.FixedLocator([0, 300, 600, 900, 1200]))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}M'))
    ax.tick_params(axis='x', labelsize=14, pad=10, length=0,
                   colors=COLORS['text_secondary'])

    ax.tick_params(axis='y', labelsize=15, pad=10, length=0,
                   colors=COLORS['text'])
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')

    ax.grid(True, axis='x',
            color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.margins(y=0.02)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing single_name_equity_volume_hrc...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'single_name_equity_volume_hrc',
                          output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
