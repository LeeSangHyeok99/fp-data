import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG

mpl.rcParams['axes.unicode_minus'] = False
# Keep SVG text editable (glyphs as <text>, not <path>)
mpl.rcParams['svg.fonttype'] = 'none'

BAR_COLOR = '#2f7dd6'
LINE_COLOR = '#ef5350'

df = pd.read_csv('outputs/data/banks_gdp_by_country.csv')
labels = df['country'].tolist()
banks = df['banks'].tolist()
gdp = df['gdp_trillion'].tolist()


def gradient_rect_bar(ax, x_center, width, height, color, alpha=0.95):
    if height is None or height <= 0:
        return
    x_left = x_center - width / 2
    x_right = x_center + width / 2
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.25 + 0.75 * (frac ** 0.5)
        gradient[i, 0] = [r * factor, g * factor, b * factor, alpha]
    ax.imshow(gradient, aspect='auto', origin='lower',
              extent=[x_left, x_right, 0, height],
              zorder=3, interpolation='bilinear')


fig, ax = create_figure('bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(labels))
bar_width = 0.55

for xi, v in zip(x, banks):
    gradient_rect_bar(ax, x_center=xi, width=bar_width, height=v, color=BAR_COLOR)

# Bar value labels: place above bar by default, but lift above the GDP line marker
# when they would otherwise collide. (Line stays on top visually.)
GDP_MAX = 30
BANK_MAX = 5000
SAFE_GAP = 350
for xi, v, gdp_v, name in zip(x, banks, gdp, labels):
    line_y = gdp_v / GDP_MAX * BANK_MAX
    base = v + 200
    label_y = max(base, line_y + SAFE_GAP) if abs(base - line_y) < SAFE_GAP else base
    label_y = min(label_y, BANK_MAX - 100)
    slug = name.lower().replace(' ', '_')
    t = ax.text(xi, label_y, f'{v:,}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color=COLORS['text_secondary'], zorder=5)
    t.set_gid(f'bank-label-{slug}')
    t.set_clip_on(False)  # allow free movement in Figma without being clipped

# Left axis (banks)
ax.set_ylim(0, 5000)
ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{int(v):,}'))

# Right axis (GDP)
ax2 = ax.twinx()
ax2.plot(x, gdp, color=LINE_COLOR, linewidth=2.2, linestyle=(0, (5, 2)),
         marker='D', markersize=9, markerfacecolor=LINE_COLOR, markeredgecolor='none',
         zorder=4)
ax2.set_ylim(0, 30)
ax2.set_yticks([0, 6, 12, 18, 24, 30])
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${int(v)}T'))

# X-axis
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlim(-0.5, len(labels) - 0.5)

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=18, length=0, pad=15, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=16, length=6, width=1, pad=10,
               rotation=0, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

ax2.tick_params(axis='y', labelsize=18, length=0, pad=15, colors=COLORS['text_secondary'])
for label in ax2.get_yticklabels():
    label.set_fontweight('bold')

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax2.grid(False)

for spine in ax.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

output_dir = 'outputs/charts/banking/global'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/banks_gdp_by_country.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/banks_gdp_by_country.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/banks_gdp_by_country.png")
