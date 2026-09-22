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
# Load pre-computed AUM data (from btc_etf_aum_stacked.py)
# =============================================================================
aum = pd.read_csv('outputs/data/btc_etf_aum_daily.csv', parse_dates=['Date'])
latest = aum.iloc[-1]

labels = ['IBIT', 'FBTC', 'GBTC', 'BITB', 'ARKB']
colors = [
    '#1f3a8a',  # IBIT navy
    '#2f6bff',  # FBTC blue
    '#6aa3ff',  # GBTC light blue
    '#f4b99a',  # BITB peach
    '#ef7a55',  # ARKB orange
]
values = [latest[c] for c in labels]

# =============================================================================
# Chart
# =============================================================================
fig, ax = create_figure('bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(labels))
bar_width = 0.55
ax.bar(x, values, width=bar_width, color=colors, edgecolor='none', zorder=3)

# Y-axis: $B
def billions_formatter(v, pos):
    return f'${v:.0f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.set_ylim(0, 80)
ax.set_yticks([0, 20, 40, 60, 80])

# X-axis
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlim(-0.5, len(labels) - 0.5)

# Style
apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=16, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Save
output_dir = 'outputs/charts/bitcoin/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/btc_etf_aum_bar.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_aum_bar.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/btc_etf_aum_bar.png")

# =============================================================================
# Stats
# =============================================================================
total = sum(latest[c] for c in labels + ['Others'])
print(f"\n--- Spot BTC ETF AUM Snapshot ({latest['Date'].date()}) ---")
for c in labels + ['Others']:
    print(f"  {c:8s}: ${latest[c]:6.1f}B  ({latest[c]/total*100:.1f}%)")
print(f"  {'Total':8s}: ${total:6.1f}B")
