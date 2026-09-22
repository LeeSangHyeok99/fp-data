import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Load data
# =============================================================================
df = pd.read_csv('outputs/data/rwa_asset_launches_by_year.csv')

categories = [
    'Stablecoins', 'Treasuries', 'Commodities', 'PrivateCredit',
    'nonUSGovDebt', 'TokenizedStocks', 'ActiveStrategies', 'RWAInfra',
    'CorpBonds', 'PrivateEquity', 'RealEstate'
]

# Pantera-style muted earth-tone palette adapted for four-pillars dark theme
cat_colors = {
    'Stablecoins':      '#8a6e44',
    'Treasuries':       '#3f6b75',
    'Commodities':      '#5d7d5b',
    'PrivateCredit':    '#a99cba',
    'nonUSGovDebt':     '#d6a99b',
    'TokenizedStocks':  '#c1a685',
    'ActiveStrategies': '#d4c084',
    'RWAInfra':         '#3f5366',
    'CorpBonds':        '#8d4444',
    'PrivateEquity':    '#86b0a8',
    'RealEstate':       '#a9b5c5',
}

LINE_COLOR = '#c9a84c'

years = df['Year'].astype(str).tolist()
x = np.arange(len(years))

# =============================================================================
# Figure
# =============================================================================
fig, ax = create_figure('stacked_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Stacked bar
bottom = np.zeros(len(years))
bar_width = 0.62
for cat in categories:
    vals = df[cat].values.astype(float)
    ax.bar(x, vals, bottom=bottom, color=cat_colors[cat],
           width=bar_width, linewidth=0, zorder=2)
    bottom += vals

totals = df[categories].sum(axis=1).values

# Left Y axis (counts)
ax.set_ylim(0, 200)
ax.set_yticks([0, 50, 100, 150, 200])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{int(v)}'))

# X axis
ax.set_xticks(x)
ax.set_xticklabels(years)
ax.set_xlim(-0.7, len(years) - 0.3)

# Apply base style
apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='x', rotation=0, labelsize=14, length=0, pad=10,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='y', labelsize=16, length=0, pad=12,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

ax.grid(True, axis='y', color=COLORS['grid'], alpha=0.45,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

# =============================================================================
# Right axis: On-chain value line
# =============================================================================
ax2 = ax.twinx()
ax2.set_facecolor('none')

oc_value_b = df['OnchainValueUSD'].values / 1e9  # USD -> $B

# Use NaN for plotting where value is 0 (2014) so the line starts from 2017
plot_values = np.where(oc_value_b > 0, oc_value_b, np.nan)

ax2.plot(x, plot_values, color=LINE_COLOR, linewidth=3.0,
         marker='o', markersize=7, markerfacecolor=LINE_COLOR,
         markeredgecolor=LINE_COLOR, zorder=6)

# Right Y axis
ax2.set_ylim(0, 400)
ax2.set_yticks([0, 100, 200, 300, 400])
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${int(v)}B'))

ax2.tick_params(axis='y', labelsize=16, length=0, pad=12,
                colors=COLORS['text_secondary'])
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.grid(False)

# Annotate on-chain values near markers
def fmt_value(v_usd):
    if v_usd <= 0:
        return ''
    if v_usd < 1e6:
        return f'${v_usd/1e3:.1f}K'
    if v_usd < 1e9:
        return f'${v_usd/1e6:.1f}M'
    return f'${v_usd/1e9:.1f}B'

raw_usd = df['OnchainValueUSD'].values
# Map bar tops to data coords on right axis to decide vertical offset for labels
bar_tops = totals
# Convert left-axis count to a notional right-axis value (counts and $B share same numeric scale via axis transforms)
for xi, vb, raw, tot in zip(x, plot_values, raw_usd, bar_tops):
    if np.isnan(vb):
        continue
    label = fmt_value(raw)
    ax2.annotate(label, xy=(xi, vb),
                 xytext=(0, 22), textcoords='offset points',
                 ha='center', va='bottom',
                 fontsize=11, fontweight='bold',
                 color=COLORS['text'], zorder=7)

# =============================================================================
# Save
# =============================================================================
output_dir = 'outputs/charts/rwa/launches'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fname = 'rwa_asset_launches_by_year'
fig.savefig(f'{output_dir}/{fname}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/{fname}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Saved: {output_dir}/{fname}.png")
print(f"Saved: {output_dir}/{fname}.svg")

# =============================================================================
# Stats
# =============================================================================
print("\n--- RWA Asset Launches by Year ---")
print(f"Years: {years[0]} ~ {years[-1]}")
print(f"Total launches: {int(totals.sum())}")
print(f"Peak year: {years[int(totals.argmax())]} ({int(totals.max())} launches)")
print(f"Latest on-chain value: ${df['OnchainValueUSD'].iloc[-1]/1e9:.1f}B")
