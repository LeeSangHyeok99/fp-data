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
df = pd.read_csv('outputs/data/crypto_payment_card_monthly_volume.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

# Convert to $M
value_cols = ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Cypher', 'Gnosis', 'Ready', 'Other']
for c in value_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0) / 1e6

# Stack order matches reference image (bottom to top):
# RedotPay (largest) first, then rest in decreasing size
stack_order = ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Cypher', 'Gnosis', 'Ready', 'Other']

# Colors matching Paymentscan reference image
CARD_COLORS = {
    'RedotPay': '#ef5f4b',   # orange-red (dominant)
    'EtherFi':  '#c42ee0',   # magenta
    'KAST':     '#1f2d88',   # dark navy
    'Karta':    '#6b1d2c',   # dark maroon
    'Tria':     '#3fbfd4',   # teal/cyan
    'Cypher':   '#f4b93a',   # yellow/gold
    'Gnosis':   '#8ac249',   # green
    'Ready':    '#f4b99a',   # peach
    'Other':    '#6b6b6b',   # gray
}

# =============================================================================
# Chart: Stacked Bar
# =============================================================================
fig, ax = create_figure('stacked_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bar_width = 0.75

bottom = np.zeros(len(df))
for card in stack_order:
    vals = df[card].values
    ax.bar(x, vals, bottom=bottom, width=bar_width,
           color=CARD_COLORS[card], edgecolor='none', zorder=3)
    bottom += vals

# Y-axis: $M
def millions_formatter(v, pos):
    return f'${v:.0f}M'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions_formatter))
ax.set_ylim(0, 800)
ax.set_yticks([0, 200, 400, 600, 800])

# X-axis: show every 4 months (Mar, Jul, Nov pattern matches reference)
tick_positions = []
tick_labels = []
for i, d in enumerate(df['date']):
    if d.month in [3, 7, 11]:
        tick_positions.append(i)
        tick_labels.append(d.strftime('%b %Y'))

ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels)
ax.set_xlim(-0.5, len(df) - 0.5)

# Style
apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Save
output_dir = 'outputs/charts/crypto-payments/volume'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/paymentscan_monthly_volume.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/paymentscan_monthly_volume.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/paymentscan_monthly_volume.png")

# =============================================================================
# Stats
# =============================================================================
df['Total'] = df[value_cols].sum(axis=1)
latest = df.iloc[-1]
peak_idx = df['Total'].idxmax()
peak = df.loc[peak_idx]

print(f"\n--- Paymentscan Monthly Card Volume ---")
print(f"Range: {df['date'].min().strftime('%b %Y')} ~ {df['date'].max().strftime('%b %Y')} ({len(df)} months)")
print(f"Peak:   {peak['date'].strftime('%b %Y')}: ${peak['Total']:,.1f}M")
print(f"Latest: {latest['date'].strftime('%b %Y')}: ${latest['Total']:,.1f}M")
print(f"\nLatest breakdown:")
for c in stack_order:
    share = latest[c] / latest['Total'] * 100
    print(f"  {c:8s}: ${latest[c]:7.1f}M  ({share:5.1f}%)")
