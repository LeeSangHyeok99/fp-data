"""
HIP-3 Monthly Volume + MoM Growth
Grouped bar (HIP-3 Total vs xyz) + dual line (MoM %)
Four Pillars theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    setup_font, save_chart, COLORS, DPI, GRID_CONFIG,
    gradient_rounded_bar,
)

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_monthly_volume_mom.csv')
df['hip3_B'] = df['hip3_total'] / 1e9
df['xyz_B'] = df['xyz_total'] / 1e9
df['hip3_mom'] = df['hip3_total'].pct_change() * 100
df['xyz_mom'] = df['xyz_total'].pct_change() * 100

labels = ['Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26*']

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    x = np.arange(len(df))
    bar_width = 0.32

    color_hip3 = '#5470c6'
    color_xyz = '#91cc75'

    # ─── Bars: Monthly Volume ───────────────────────────────────────
    for i, (hip3_v, xyz_v) in enumerate(zip(df['hip3_B'], df['xyz_B'])):
        gradient_rounded_bar(ax, x[i] - bar_width/2, bar_width, hip3_v, color=color_hip3)
        gradient_rounded_bar(ax, x[i] + bar_width/2, bar_width, xyz_v, color=color_xyz)

    # Bar value labels
    for i, (hip3_v, xyz_v) in enumerate(zip(df['hip3_B'], df['xyz_B'])):
        if hip3_v >= 1:
            label = f'${hip3_v:.1f}B'
        else:
            label = f'${hip3_v*1000:.0f}M'
        ax.text(x[i] - bar_width/2, hip3_v + 1.2, label,
                ha='center', va='bottom', fontsize=13, fontweight='bold',
                color=color_hip3, zorder=6)

        if xyz_v >= 1:
            label = f'${xyz_v:.1f}B'
        else:
            label = f'${xyz_v*1000:.0f}M'
        ax.text(x[i] + bar_width/2, xyz_v + 1.2, label,
                ha='center', va='bottom', fontsize=13, fontweight='bold',
                color=color_xyz, zorder=6)

    # ─── Line: MoM Growth (right Y axis) ───────────────────────────
    ax2 = ax.twinx()

    mom_hip3 = df['hip3_mom'].values
    mom_xyz = df['xyz_mom'].values

    # Only plot from month 2 onwards (first month has no MoM)
    valid = ~np.isnan(mom_hip3)
    ax2.plot(x[valid], mom_hip3[valid], color=color_hip3, linewidth=2.5,
             linestyle='--', marker='o', markersize=8, zorder=5, alpha=0.8)
    ax2.plot(x[valid], mom_xyz[valid], color=color_xyz, linewidth=2.5,
             linestyle='--', marker='o', markersize=8, zorder=5, alpha=0.8)

    # MoM labels
    for i in range(len(df)):
        if not np.isnan(mom_hip3[i]):
            ax2.text(x[i] - 0.08, mom_hip3[i] + 15, f'{mom_hip3[i]:.0f}%',
                     ha='center', va='bottom', fontsize=12, fontweight='bold',
                     color=color_hip3, alpha=0.8, zorder=6)
        if not np.isnan(mom_xyz[i]):
            ax2.text(x[i] + 0.08, mom_xyz[i] - 15, f'{mom_xyz[i]:.0f}%',
                     ha='center', va='top', fontsize=12, fontweight='bold',
                     color=color_xyz, alpha=0.8, zorder=6)

    # ─── Left Y axis (Volume) ──────────────────────────────────────
    ax.set_ylim(0, 70)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 14, 28, 42, 56, 70]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}B'))
    ax.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=COLORS['text_secondary'])

    # ─── Right Y axis (MoM %) ──────────────────────────────────────
    ax2.set_ylim(0, 700)
    n_ticks = 6
    right_ticks = np.linspace(0, 700, n_ticks)
    ax2.yaxis.set_major_locator(mticker.FixedLocator(right_ticks))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax2.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=COLORS['text_secondary'])
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)

    # ─── X axis ─────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=16, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.tick_params(axis='x', length=0, pad=12)

    # ─── Grid ───────────────────────────────────────────────────────
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    ax2.grid(False)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xlim(-0.6, len(df) - 0.4)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing hip3_monthly_volume_mom...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_monthly_volume_mom', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
