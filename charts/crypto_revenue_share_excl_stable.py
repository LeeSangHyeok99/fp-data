import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, SERIES_COLORS, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data (Sealaunch / DefiLlama)
# ══════════════════════════════════════════════════
df = pd.read_csv('outputs/data/sealaunch_revenue_by_category.csv')
df['date'] = pd.to_datetime(df['date'])

# Drop last partial month (Mar 2026)
df = df.iloc[:-1]

# Exclude Stablecoin Issuer, compute shares
cats_exclude = ['Stablecoin Issuer']
cats = [c for c in df.columns if c not in ['date'] + cats_exclude]

# Merge small categories into "Other"
top_cats = ['Derivatives', 'Dexs', 'Launchpad', 'Trading App', 'Lending', 'Wallets', 'CDP']
other_cats = [c for c in cats if c not in top_cats and c != 'Other']

df['Other_merged'] = df['Other'] + df[other_cats].sum(axis=1)
plot_cats = top_cats + ['Other_merged']
plot_labels = top_cats + ['Other']

# Compute share percentages
totals = df[cats].sum(axis=1)
shares = pd.DataFrame()
shares['date'] = df['date']
for i, cat in enumerate(plot_cats):
    label = plot_labels[i]
    if cat == 'Other_merged':
        shares[label] = df['Other_merged'] / totals * 100
    else:
        shares[label] = df[cat] / totals * 100

x = shares['date'].values

# ══════════════════════════════════════════════════
# Colors
# ══════════════════════════════════════════════════
colors = [
    '#E07B7B',  # Derivatives - warm red
    '#5470c6',  # Dexs - blue
    '#fac858',  # Launchpad - yellow
    '#91cc75',  # Trading App - green
    '#73c0de',  # Lending - light blue
    '#fc8452',  # Wallets - orange
    '#9a60b4',  # CDP - purple
    '#555555',  # Other - gray
]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Stacked area
# ══════════════════════════════════════════════════
series = [shares[label].values for label in plot_labels]
ax.stackplot(x, *series, colors=colors, alpha=0.8, edgecolor='none', linewidth=0)

# Draw boundary lines
bottom = np.zeros(len(shares))
for i, label in enumerate(plot_labels):
    bottom = bottom + shares[label].values
    ax.plot(x, bottom, color=colors[i], linewidth=0.8, alpha=0.9)

# ══════════════════════════════════════════════════
# Y-axis (max 5 ticks)
# ══════════════════════════════════════════════════
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'crypto_revenue_share_excl_stable',
                                'outputs/charts/crypto-revenue')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
