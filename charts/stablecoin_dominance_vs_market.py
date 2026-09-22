"""
Stablecoin Dominance vs Crypto Market Cap - Dual Axis
Shows "flight to stability" pattern: crypto -21%, dominance 9%→13%
Compares to 2022 bear market pattern
Source: CEX.IO, DefiLlama
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS, area_glow, endpoint_dot

# ── Data ──
df = pd.read_csv('outputs/data/stablecoin_dominance_timeline.csv')
df['date'] = pd.to_datetime(df['date'])
dates = df['date']
dominance = df['stablecoin_dominance_pct']
crypto_mcap = df['crypto_mcap_t']

# ── Chart ──
fig, ax1 = create_figure('line')

# Crypto market cap (area, left axis)
mcap_color = '#5470c6'
ax1.fill_between(dates, 0, crypto_mcap, color=mcap_color, alpha=0.15, linewidth=0)
ax1.plot(dates, crypto_mcap, color=mcap_color, linewidth=2.5, alpha=0.9)
endpoint_dot(ax1, dates.iloc[-1], crypto_mcap.iloc[-1], mcap_color)

# Left Y axis
y1_ticks = [0, 1, 2, 3, 4]
ax1.set_yticks(y1_ticks)
ax1.set_yticklabels([f'{v}T' for v in y1_ticks])
ax1.set_ylim(0, 4.5)

# Dominance line (right axis)
ax2 = ax1.twinx()
dom_color = '#fac858'
ax2.plot(dates, dominance, color=dom_color, linewidth=3, zorder=5)
endpoint_dot(ax2, dates.iloc[-1], dominance.iloc[-1], dom_color, size=70)

# Dominance labels at key points
key_points = [
    (2, '8%'),    # 2022-01 start
    (5, '17%'),   # 2022-10 peak
    (12, '9%'),   # 2026-01
    (17, '13%'),  # 2026-03 current
]
for idx, label in key_points:
    if idx < len(dates):
        ax2.annotate(label,
                     xy=(dates.iloc[idx], dominance.iloc[idx]),
                     xytext=(0, 15), textcoords='offset points',
                     fontsize=14, fontweight='bold', color=dom_color,
                     ha='center')

# Right Y axis
y2_ticks = [0, 5, 10, 15, 20]
ax2.set_yticks(y2_ticks)
ax2.set_yticklabels([f'{v}%' for v in y2_ticks])
ax2.set_ylim(0, 22)

# Highlight 2022 and 2026 zones
from matplotlib.patches import FancyBboxPatch
# 2022 zone
ax1.axvspan(pd.Timestamp('2022-04-01'), pd.Timestamp('2022-10-01'),
            alpha=0.08, color='#ef5350', zorder=0)
ax1.text(pd.Timestamp('2022-07-01'), 4.2, '2022',
         ha='center', fontsize=12, fontweight='bold', color='#ef5350', alpha=0.7)

# 2026 zone
ax1.axvspan(pd.Timestamp('2026-01-01'), pd.Timestamp('2026-03-31'),
            alpha=0.08, color='#ef5350', zorder=0)
ax1.text(pd.Timestamp('2026-02-15'), 4.2, 'Q1 2026',
         ha='center', fontsize=12, fontweight='bold', color='#ef5350', alpha=0.7)

# X axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

apply_style(fig, ax1, 'line')

# ax2 styling
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=dom_color)
ax2.grid(False)

fig.tight_layout()

output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_dominance_vs_market', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_dominance_vs_market.png')
