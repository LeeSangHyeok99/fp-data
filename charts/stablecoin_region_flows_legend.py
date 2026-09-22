import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS

# standalone legend strip for the region flows heatmap: same Blues_r scale,
# Low (dark) on the left, High (light) on the right, log scale.
# Positions are measured from actual rendered text widths (in inches) so
# elements never overlap regardless of font metrics.

setup_font()
FIG_H = 0.62
fig = plt.figure(figsize=(9.5, FIG_H), dpi=150)
fig.patch.set_alpha(0)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor('none')
ax.axis('off')

# work in inches: 1 data unit = 1 inch on this axes
ax.set_xlim(0, fig.get_figwidth())
ax.set_ylim(0, fig.get_figheight())

y_mid = FIG_H / 2
gap = 0.14


def add_text(x, s, color, fontsize=13):
    t = ax.text(x, y_mid, s, ha='left', va='center', fontsize=fontsize,
                 fontweight='bold', color=color, zorder=4)
    fig.canvas.draw()
    bbox = t.get_window_extent(renderer=fig.canvas.get_renderer())
    width_in = bbox.width / fig.dpi
    return x + width_in


x = 0.0
x = add_text(x, 'Sender (Row) → Receiver (Column)', COLORS['text_secondary'])
x += gap * 2.2
x = add_text(x, 'Low', COLORS['text'])
x += gap

bar_x0 = x
bar_w = 1.05
bar_h = 0.24
bar_y0 = y_mid - bar_h / 2
bar_x1 = bar_x0 + bar_w

cmap = plt.get_cmap('Blues_r')
gradient = np.repeat(np.linspace(0, 1, 256).reshape(1, -1), 2, axis=0)

box = FancyBboxPatch((bar_x0, bar_y0), bar_w, bar_h,
                      boxstyle='round,pad=0,rounding_size=0.05',
                      facecolor='none', edgecolor='none')
ax.add_patch(box)
im = ax.imshow(gradient, cmap=cmap, aspect='auto',
                extent=[bar_x0, bar_x1, bar_y0, bar_y0 + bar_h],
                zorder=3, interpolation='bilinear')
im.set_clip_path(box)

x = bar_x1 + gap
x = add_text(x, 'High (Log Scale)', COLORS['text'])

ax.set_xlim(0, x + 0.05)
ax.set_ylim(0, FIG_H)
fig.set_size_inches(x + 0.05, FIG_H)

output_dir = Path('outputs/charts/stablecoin/regional_flows')
output_dir.mkdir(parents=True, exist_ok=True)
svg_path = output_dir / 'stablecoin_region_flows_legend.svg'
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            transparent=True)
plt.close(fig)

print(svg_path)
