"""
HIP-3 Monthly Volume + MoM Growth
Grouped bar (HIP-3 Total vs xyz) + dual line (MoM %)
HRC theme + Hyperliquid brand colors
"""

import sys
sys.path.insert(0, '.claude/skills/design/hrc')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from pathlib import Path
from config import (
    setup_font, save_chart, COLORS, DPI, GRID_CONFIG,
)

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Hyperliquid brand colors ──────────────────────────────────────────
COLOR_HIP3 = '#50e3c2'   # Hyperliquid teal
COLOR_XYZ = '#2d8c6f'    # Deep green

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_monthly_volume_v4.csv')
df['hip3_B'] = df['hip3_total_volume'] / 1e9
df['xyz_B'] = df['xyz_volume'] / 1e9

# Parse MoM growth from string (e.g. "+83.2%") to float
def parse_mom(s):
    if pd.isna(s) or s == '':
        return np.nan
    return float(str(s).replace('%', '').replace('+', ''))

df['hip3_mom'] = df['hip3_mom_growth'].apply(parse_mom)
df['xyz_mom'] = df['xyz_mom_growth'].apply(parse_mom)

labels = ['Nov 2025', 'Dec 2025', 'Jan 2026', 'Feb 2026', 'Mar 2026*']


# ─── Gradient rounded bar ──────────────────────────────────────────────
def gradient_rounded_bar(ax, x_center, width, height, color, alpha=0.95):
    if height is None or height <= 0:
        return
    radius = min(width / 2, height * 0.35)
    rect_top = height - radius
    x_left = x_center - width / 2
    x_right = x_center + width / 2

    theta = np.linspace(0, np.pi, 40)
    arc_x = x_center + radius * np.cos(theta)
    arc_y = rect_top + radius * np.sin(theta)

    verts = [(x_left, 0), (x_right, 0), (x_right, rect_top)]
    for px, py in zip(arc_x, arc_y):
        verts.append((px, py))
    verts.append((x_left, rect_top))
    verts.append((x_left, 0))

    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    path = MPath(verts, codes)
    clip_patch = PathPatch(path, facecolor='none', edgecolor='none',
                           transform=ax.transData)
    ax.add_patch(clip_patch)

    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.15 + 0.85 * (frac ** 0.5)
        gradient[i, 0] = [r * factor, g * factor, b * factor, alpha]

    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, height],
                   zorder=3, interpolation='bilinear')
    im.set_clip_path(clip_patch)


# ─── Draw ───────────────────────────────────────────────────────────────
def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    x = np.arange(len(df))
    bar_width = 0.32

    # ─── Bars: Monthly Volume ───────────────────────────────────────
    for i, (hip3_v, xyz_v) in enumerate(zip(df['hip3_B'], df['xyz_B'])):
        gradient_rounded_bar(ax, x[i] - bar_width/2, bar_width, hip3_v, color=COLOR_HIP3)
        gradient_rounded_bar(ax, x[i] + bar_width/2, bar_width, xyz_v, color=COLOR_XYZ)

    # Bar value labels removed

    # ─── Line: MoM Growth (right Y axis) ───────────────────────────
    ax2 = ax.twinx()

    mom_hip3 = df['hip3_mom'].values
    mom_xyz = df['xyz_mom'].values

    valid = ~np.isnan(mom_hip3)
    ax2.plot(x[valid], mom_hip3[valid], color=COLOR_HIP3, linewidth=2.5,
             linestyle='--', marker='o', markersize=8, zorder=5, alpha=0.7)
    ax2.plot(x[valid], mom_xyz[valid], color=COLOR_XYZ, linewidth=2.5,
             linestyle='--', marker='o', markersize=8, zorder=5, alpha=0.7)

    # MoM labels removed to avoid overlap with bar labels
    # Dashed lines convey the trend visually

    # ─── Left Y axis (Volume) ──────────────────────────────────────
    ax.set_ylim(0, 60)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30, 40, 50, 60]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}B'))
    ax.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=COLORS['text_secondary'])

    # ─── Right Y axis (MoM %) ──────────────────────────────────────
    ax2.set_ylim(0, 250)
    right_ticks = np.arange(0, 251, 50)
    ax2.yaxis.set_major_locator(mticker.FixedLocator(right_ticks))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}%'))
    ax2.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=COLORS['text_secondary'])
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # ─── X axis ─────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=18, fontweight='bold',
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
    print('Drawing hip3_monthly_volume_mom (HRC)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_monthly_volume_mom_hrc', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
