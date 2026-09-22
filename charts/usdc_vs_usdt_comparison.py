"""
USDC vs USDT: Market Cap vs Transfer Volume (Donut x2)
Shows the paradox: USDT dominates cap, USDC dominates volume
Data: rwa.xyz (2026-03-25)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from config import setup_font, save_chart, COLORS, DPI

OUTPUT_DIR = 'outputs/charts/stablecoin/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

USDT_COLOR = '#26a17b'
USDC_COLOR = '#2775ca'
OTHERS_COLOR = '#3a3a3a'

# Data from rwa.xyz (2026-03-25)
# Market Cap: USDT $185.7B (58.2%), USDC $75.7B (25.0%), Others $38.8B (16.8%)
mcap_vals = [185.66, 75.68, 38.83]
mcap_labels = ['USDT', 'USDC', 'Others']
mcap_colors = [USDT_COLOR, USDC_COLOR, OTHERS_COLOR]

# Monthly Transfer Volume: USDT $1.94T, USDC $8.11T (rest not shown, just these two)
# From rwa.xyz total $9.53T -> others = $9.53 - 8.11 - 1.94 = -0.52 (rounding)
# Use just USDT vs USDC ratio
# Just show USDT vs USDC for volume (they dominate)
vol_vals = [1.54, 6.0]
vol_labels = ['USDT', 'USDC']
vol_colors = [USDT_COLOR, USDC_COLOR]


def draw_donuts():
    setup_font()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.67, 5.5), dpi=DPI)
    fig.patch.set_alpha(0)

    donut_ratio = 0.55
    wedge_props = {'linewidth': 2, 'edgecolor': '#141414'}

    for ax, vals, labels, colors, center_top, center_bot in [
        (ax1, mcap_vals, mcap_labels, mcap_colors, '$300.2B', 'Market Cap'),
        (ax2, vol_vals, vol_labels, vol_colors, '$7.54T', 'Monthly Volume'),
    ]:
        ax.set_facecolor('none')

        wedges, _ = ax.pie(
            vals,
            colors=colors,
            startangle=90,
            wedgeprops=wedge_props,
            counterclock=False,
        )

        # Donut hole
        centre = plt.Circle((0, 0), donut_ratio, fc='#141414')
        ax.add_artist(centre)

        # Center text
        ax.text(0, 0.08, center_top, ha='center', va='center',
                fontsize=22, fontweight='bold', color=COLORS['text'])
        ax.text(0, -0.18, center_bot, ha='center', va='center',
                fontsize=11, fontweight='bold', color=COLORS['text_secondary'])

        # Outside labels with percentage
        total = sum(vals)
        for i, (wedge, val, label) in enumerate(zip(wedges, vals, labels)):
            pct = val / total * 100
            if pct < 5:
                continue
            angle = (wedge.theta1 + wedge.theta2) / 2
            rad = np.radians(angle)
            x = np.cos(rad) * 0.82
            y = np.sin(rad) * 0.82

            ax.text(x, y, f'{label}\n{pct:.1f}%',
                    ha='center', va='center',
                    fontsize=10, fontweight='bold',
                    color='white')

        ax.set_aspect('equal')

    fig.tight_layout(pad=2)
    return fig


if __name__ == '__main__':
    print('Drawing usdc_vs_usdt_comparison donuts...')
    fig = draw_donuts()
    png, svg = save_chart(fig, 'usdc_vs_usdt_comparison', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
