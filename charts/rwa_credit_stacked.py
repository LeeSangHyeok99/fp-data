import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Load
# =============================================================================
df = pd.read_csv('outputs/data/rwa_credit_all_daily.csv', parse_dates=[0], index_col=0)

# Pick top series to plot, collapse remainder as Others
top_series = [
    'Figure HELOC Token',
    'Syrup USDC',
    'Syrup USDT',
    'Blockstream Mining Note 2',
    'PKH Mining Note 2',
]
other_cols = [c for c in df.columns if c not in top_series]
plot_df = df[top_series].copy()
plot_df['Others'] = df[other_cols].sum(axis=1)

# Trim to Jan 2022 onward
plot_df = plot_df[plot_df.index >= '2022-01-01']

# Convert to $B
plot_df = plot_df / 1e9

# =============================================================================
# Chart (stacked area)
# =============================================================================
fig, ax = create_figure('stacked')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Muted palette (softer saturation)
colors = [
    '#8b7fd1',   # Figure HELOC muted purple
    '#d9a35f',   # Syrup USDC muted orange
    '#c98265',   # Syrup USDT warm clay
    '#6db3bc',   # Blockstream muted cyan
    '#6fa898',   # PKH muted teal
    '#7a7a7a',   # Others gray
]

labels = top_series + ['Others']
values = [plot_df[c].values for c in labels]

# Stacked area with gradient: draw each layer with vertical gradient (darker bottom, lighter top)
import matplotlib.colors as mcolors
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

xdates = plot_df.index
x_num = mpl.dates.date2num(xdates)

cumulative = np.zeros(len(plot_df))
for color, col in zip(colors, labels):
    vals = plot_df[col].values
    top = cumulative + vals
    verts = list(zip(x_num, cumulative)) + list(zip(x_num[::-1], top[::-1]))
    poly_path = MPath(verts + [verts[0]])
    patch = PathPatch(poly_path, facecolor='none', edgecolor='none', zorder=2)
    ax.add_patch(patch)

    # Per-layer gradient: bright/saturated at top edge, darker at bottom
    r, g, b = mcolors.to_rgb(color)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.55 + 0.45 * frac
        grad[i, 0] = [r * factor, g * factor, b * factor, 1.0]

    y_lo = float(np.nanmin(cumulative))
    y_hi = float(np.nanmax(top))
    if y_hi > y_lo:
        im = ax.imshow(grad, aspect='auto', origin='lower',
                       extent=[x_num[0], x_num[-1], y_lo, y_hi],
                       zorder=2, interpolation='bilinear')
        im.set_clip_path(patch)

    cumulative = top

# Y-axis: $B
def billions_formatter(v, pos):
    return f'${v:.0f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.set_ylim(0, 30)
ax.set_yticks([0, 10, 20, 30])

# X-axis: yearly
ax.xaxis.set_major_locator(YearLocator(base=1, month=1, day=1))
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
ax.set_xlim(plot_df.index.min(), plot_df.index.max())

# Style
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Save
output_dir = 'outputs/charts/rwa/credit'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/rwa_credit_stacked.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/rwa_credit_stacked.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/rwa_credit_stacked.png")

# =============================================================================
# Stats
# =============================================================================
latest = plot_df.iloc[-1]
total_latest = latest.sum()
print(f"\n--- Tokenized Credit (All) ---")
print(f"Range: {plot_df.index.min().date()} ~ {plot_df.index.max().date()}")
print(f"Total latest: ${total_latest:.2f}B")
print(f"\nLatest breakdown:")
for c in labels:
    share = latest[c] / total_latest * 100
    print(f"  {c[:45]:45s}: ${latest[c]:6.2f}B  ({share:5.1f}%)")
