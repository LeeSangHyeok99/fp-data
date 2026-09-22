"""
MakerDAO/Sky Smart Burn Engine (SBE) Surplus Redirect
Horizontal bar: Pre-Cut vs Post-Cut vs Redirected to Surplus
Four Pillars theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    setup_font, save_chart, COLORS, DPI,
    GRID_CONFIG, gradient_rounded_bar,
)

OUTPUT_DIR = 'outputs/charts/makerdao/sbe'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Data
categories = ['SBE Pre-Cut', 'SBE Post-Cut', 'Redirected to Surplus']
values = [110.0, 13.7, 96.3]
colors = ['#ef5350', '#787b86', '#26a69a']


def draw_horizontal_bar():
    setup_font()
    fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    y_pos = np.array([2, 1, 0])
    bar_height = 0.35

    import matplotlib.colors as mcolors
    from matplotlib.patches import FancyBboxPatch

    for i, (y, val, color) in enumerate(zip(y_pos, values, colors)):
        r, g, b = mcolors.to_rgb(color)

        # Gradient image clipped to bar shape
        gradient = np.zeros((1, 256, 4))
        for j in range(256):
            frac = j / 255
            factor = 0.25 + 0.75 * (frac ** 0.5)
            gradient[0, j] = [r * factor, g * factor, b * factor, 0.95]

        extent = [0, val, y - bar_height / 2, y + bar_height / 2]
        im = ax.imshow(gradient, aspect='auto', origin='lower',
                       extent=extent, zorder=3, interpolation='bilinear')

        # Value label
        ax.text(val + 2, y, f'${val:.1f}M/yr',
                ha='left', va='center',
                fontsize=14, fontweight='bold',
                color=color)

    # Y axis labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=13, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.tick_params(axis='y', length=0, pad=15)

    # X axis
    ax.set_xlim(0, 140)
    ax.xaxis.set_major_locator(mticker.FixedLocator([0, 30, 60, 90, 120]))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}M'))
    ax.tick_params(axis='x', labelsize=11, pad=8, length=0,
                   colors=COLORS['text_secondary'])

    # Grid
    ax.grid(True, axis='x', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylim(-0.5, 2.7)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing sbe_surplus_redirect...')
    fig = draw_horizontal_bar()
    png, svg = save_chart(fig, 'sbe_surplus_redirect', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
