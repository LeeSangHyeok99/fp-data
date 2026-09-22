import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, save_chart, setup_font, COLORS

df = pd.read_csv('sources/region-to-region-flows.csv', index_col=0)

REGIONS = ['Asia-Pacific', 'North America', 'Middle East & Africa', 'Europe', 'Latin America']
COL_LABEL = {
    'Asia-Pacific': 'APAC',
    'North America': 'N. America',
    'Middle East & Africa': 'MEA',
    'Europe': 'Europe',
    'Latin America': 'LatAm',
}

matrix = df.loc[REGIONS, REGIONS].to_numpy(dtype=float)
stays_pct = df.loc[REGIONS, 'stays_in_region_pct'].to_numpy(dtype=float)


def fmt_usd(v):
    if v >= 1e9:
        return f'${v / 1e9:.2f}B'
    if v >= 1e8:
        return f'${v / 1e6:.0f}M'
    return f'${v / 1e6:.1f}M'


setup_font()
# wider-than-tall figure so the grid reads as a landscape panel, not a square
fig, ax = plt.subplots(figsize=(14.5, 5.6), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

n = len(REGIONS)
norm = mcolors.LogNorm(vmin=matrix.min(), vmax=matrix.max())
# bigger flows = darker/more saturated, smaller flows = lighter. More
# intuitive at a glance ("more ink = more money") than the inverted mapping
cmap = plt.get_cmap('Blues')

# rounded-corner cells drawn individually (instead of imshow) so the gaps
# between them show the real background rather than hard white gridlines
margin = 0.05
for i in range(n):
    for j in range(n):
        val = matrix[i, j]
        frac = norm(val)
        color = cmap(frac)
        is_diag = i == j
        box = FancyBboxPatch(
            (j - 0.5 + margin, i - 0.5 + margin), 1 - 2 * margin, 1 - 2 * margin,
            boxstyle='round,pad=0,rounding_size=0.07',
            facecolor=color, edgecolor=COLORS['text_secondary'] if is_diag else 'none',
            linewidth=2 if is_diag else 0, zorder=2)
        ax.add_patch(box)

        # big values render dark, so they need light text; small values
        # render light and need dark text
        text_color = '#ffffff' if frac > 0.55 else COLORS['text_secondary']
        ax.text(j, i, fmt_usd(val), ha='center', va='center',
                fontsize=17, fontweight='bold', color=text_color, zorder=4)

# stays-in-region % to the right of the grid
for i in range(n):
    ax.text(n - 0.15, i, f'{stays_pct[i]:.1f}%', ha='left', va='center',
            fontsize=19, fontweight='bold', color=COLORS['text'], zorder=4)

ax.set_xticks(range(n))
ax.set_xticklabels([COL_LABEL[r] for r in REGIONS], fontsize=18,
                    fontweight='bold', color=COLORS['text_secondary'])
ax.xaxis.set_ticks_position('top')
ax.xaxis.set_label_position('top')
ax.tick_params(axis='x', length=0, pad=10)

ax.set_yticks(range(n))
ax.set_yticklabels(REGIONS, fontsize=18, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

ax.set_xlim(-0.5, n + 0.5)
ax.set_ylim(n - 0.5, -0.5)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

Path('outputs/charts/stablecoin/regional_flows').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'stablecoin_region_flows_heatmap',
                                 'outputs/charts/stablecoin/regional_flows')
plt.close(fig)

print(png_path)
print(svg_path)
