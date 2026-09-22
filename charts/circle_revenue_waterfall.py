"""
Circle Revenue-to-EBITDA Waterfall Chart
Vertical cascade: Revenue → Distribution Costs → RLDC → OpEx → Adj. EBITDA
Four Pillars theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, FancyBboxPatch
from pathlib import Path
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

OUTPUT_DIR = 'outputs/charts/circle/financials'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Data ───────────────────────────────────────────────────────────────
# Waterfall steps
steps = [
    {
        'label': 'Total Revenue',
        'bars': [
            {'value': 2.64, 'color': '#ee6666', 'label': '$2.64B'},
            {'value': 0.11, 'color': '#5470c6', 'label': '$0.11B'},
        ],
        'total_label': '$2.75B',
        'annotation': None,
        'top_labels': True,
    },
    {
        'label': 'Distribution\nCosts',
        'bars': [
            {'value': 1.08, 'color': '#787b86', 'hatch': None, 'label': '$1.08B'},
            {'value': 1.66, 'color': '#ef5350', 'hatch': '///', 'label': '-$1.66B'},
        ],
        'total_label': None,
        'annotation': None,
        'top_labels': False,
    },
    {
        'label': 'RLDC',
        'bars': [
            {'value': 1.08, 'color': '#8B8532', 'label': '$1.08B'},
        ],
        'total_label': None,
        'annotation': '← 39.4% margin → guided 38-40% FY26',
    },
    {
        'label': 'Adj. Operating\nExpenses',
        'bars': [
            {'value': 0.58, 'color': '#787b86', 'hatch': None, 'label': '$0.58B'},
            {'value': 0.508, 'color': '#ef5350', 'hatch': '///', 'label': '-$0.508B'},
        ],
        'total_label': None,
        'annotation': None,
        'top_labels': False,
    },
    {
        'label': 'Adj. EBITDA',
        'bars': [
            {'value': 0.58, 'color': '#26a69a', 'label': '$0.58B'},
        ],
        'total_label': None,
        'annotation': '← 44x trailing at $103/share',
    },
]

# ─── Draw ───────────────────────────────────────────────────────────────
def draw_waterfall():
    setup_font()

    fig, ax = plt.subplots(figsize=(18, 7.5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    n_rows = len(steps)
    y_positions = np.arange(n_rows)[::-1]  # top to bottom
    bar_height = 0.42
    max_x = 3.0  # scale to $3B

    for idx, (step, y) in enumerate(zip(steps, y_positions)):
        x_start = 0

        for bar_info in step['bars']:
            val = bar_info['value']
            color = bar_info['color']
            hatch = bar_info.get('hatch', None)

            # Draw bar
            r, g, b = mcolors.to_rgb(color)

            if hatch:
                # Hatched bar for costs
                rect = mpatches.FancyBboxPatch(
                    (x_start, y - bar_height / 2), val, bar_height,
                    boxstyle='round,pad=0,rounding_size=0.03',
                    facecolor=color, edgecolor=color,
                    alpha=0.35, hatch='///', zorder=3,
                    linewidth=0,
                )
                ax.add_patch(rect)

                # Hatch edge color
                rect_edge = mpatches.FancyBboxPatch(
                    (x_start, y - bar_height / 2), val, bar_height,
                    boxstyle='round,pad=0,rounding_size=0.03',
                    facecolor='none', edgecolor=color,
                    alpha=0.6, hatch='///', zorder=4,
                    linewidth=0.5,
                )
                ax.add_patch(rect_edge)

                # Label on hatched bar
                label_x = x_start + val / 2
                ax.text(label_x, y, bar_info['label'],
                        ha='center', va='center',
                        fontsize=16, fontweight='bold',
                        color='#ef5350', alpha=0.9, zorder=5)
            else:
                # Solid gradient bar
                gradient = np.zeros((1, 256, 4))
                for j in range(256):
                    frac = j / 255
                    factor = 0.3 + 0.7 * (frac ** 0.45)
                    gradient[0, j] = [r * factor, g * factor, b * factor, 0.95]

                extent = [x_start, x_start + val, y - bar_height / 2, y + bar_height / 2]
                im = ax.imshow(gradient, aspect='auto', origin='lower',
                               extent=extent, zorder=3, interpolation='bilinear')

                # Rounded clip
                rect_clip = mpatches.FancyBboxPatch(
                    (x_start, y - bar_height / 2), val, bar_height,
                    boxstyle='round,pad=0,rounding_size=0.03',
                    facecolor='none', edgecolor='none',
                    transform=ax.transData,
                )
                ax.add_patch(rect_clip)
                im.set_clip_path(rect_clip)

                # Value label on solid bar
                if step.get('total_label'):
                    # For total revenue, put label at start
                    ax.text(0.06, y, step['total_label'],
                            ha='left', va='center',
                            fontsize=22, fontweight='bold',
                            color='white', zorder=6)
                elif not step.get('top_labels', False):
                    ax.text(x_start + val / 2, y, bar_info['label'],
                            ha='center', va='center',
                            fontsize=16, fontweight='bold',
                            color='white', zorder=6)

            x_start += val

        # Top labels for revenue split
        if step.get('top_labels'):
            x_pos = 0
            for i, bar_info in enumerate(step['bars']):
                val = bar_info['value']
                label = bar_info.get('label', '')
                lbl_color = bar_info['color']

                if i == 0:
                    lbl_x = val / 2
                else:
                    lbl_x = x_pos + val / 2

                ax.text(lbl_x, y + bar_height / 2 + 0.15, label,
                        ha='center', va='bottom',
                        fontsize=14, fontweight='bold',
                        color=lbl_color, zorder=6)

                x_pos += val

        # Annotation on the right
        if step.get('annotation'):
            bar_end = sum(b['value'] for b in step['bars'])
            ax.text(bar_end + 0.08, y, step['annotation'],
                    ha='left', va='center',
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'], zorder=6)

        # Downward arrow between rows
        if idx < n_rows - 1:
            next_y = y_positions[idx + 1]
            arrow_y_start = y - bar_height / 2 - 0.05
            arrow_y_end = next_y + bar_height / 2 + 0.05
            ax.annotate('', xy=(0.15, arrow_y_end), xytext=(0.15, arrow_y_start),
                        arrowprops=dict(arrowstyle='->', color=COLORS['text_secondary'],
                                        lw=1.5, mutation_scale=15),
                        zorder=2)

    # Y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels([s['label'] for s in steps],
                       fontsize=16, fontweight='bold',
                       color=COLORS['text'], ha='right')
    ax.tick_params(axis='y', length=0, pad=15)

    # X-axis off
    ax.set_xlim(-0.02, max_x + 0.5)
    ax.set_ylim(y_positions[-1] - 0.6, y_positions[0] + 0.8)
    ax.xaxis.set_visible(False)

    # No grid for this chart type
    ax.grid(False)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing circle_revenue_waterfall...')
    fig = draw_waterfall()
    png, svg = save_chart(fig, 'circle_revenue_waterfall', output_dir=OUTPUT_DIR)
    print(f'  → {png}')
    plt.close(fig)
    print('Done.')
