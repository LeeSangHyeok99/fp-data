"""
Non-USD vs USD Stablecoin Supply Growth Comparison
Bar chart: +300% vs +130% (Jan 2023 → Feb 2026)
Four Pillars theme
Source: Dune x Visa "Beyond Dollarization" report
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    setup_font, save_chart, create_figure, apply_style,
    COLORS, DPI, GRID_CONFIG, gradient_rounded_bar,
)

OUTPUT_DIR = 'outputs/charts/stablecoin/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
categories = ['Non-USD\n(ex-EURT)', 'USD']
growth_pct = [300, 130]
colors = ['#5470c6', '#787b86']
abs_values = [('\$0.35B → \$1.1B', ''), ('', '')]


# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    fig, ax = create_figure(chart_type='bar')

    x = np.arange(len(categories))
    bar_width = 0.35

    for i, (xpos, height, color) in enumerate(zip(x, growth_pct, colors)):
        gradient_rounded_bar(ax, xpos, bar_width, height, color=color, alpha=0.95)

        # Percentage label on top of bar
        ax.text(xpos, height + 12, f'+{height}%',
                ha='center', va='bottom',
                fontsize=28, fontweight='bold',
                color=color, zorder=6)

    # ─── X axis: category + absolute values ───────────────────────
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 370)

    ax.set_xticks(x)
    ax.set_xticklabels(categories,
                       fontsize=16, fontweight='bold',
                       color=COLORS['text'])
    ax.tick_params(axis='x', length=0, pad=15)

    # Absolute value label below Non-USD only
    frac_x = (0 - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0])
    ax.text(frac_x, -0.22, abs_values[0][0],
            ha='center', va='top',
            fontsize=12, fontweight='bold',
            color=COLORS['text_secondary'],
            transform=ax.transAxes, zorder=6)

    # Y axis: percentage
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 100, 200, 300]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'{v:.0f}%'))

    apply_style(fig, ax, chart_type='bar')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')

    fig.subplots_adjust(bottom=0.25)

    return fig


if __name__ == '__main__':
    print('Drawing non_usd_vs_usd_stablecoin_growth...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'non_usd_vs_usd_stablecoin_growth', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
