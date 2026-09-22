import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG, SERIES_COLORS

# ══════════════════════════════════════════════════
# Data: x402 weekly transaction volume
# Sources: Lookonchain, AInvest, Yahoo Finance, TechFlow
# ══════════════════════════════════════════════════
dates = [
    datetime(2025, 7, 14),   # Q3 2025 launch
    datetime(2025, 8, 4),
    datetime(2025, 8, 25),
    datetime(2025, 9, 15),
    datetime(2025, 10, 6),
    datetime(2025, 10, 25),  # weekly ATH 156K
    datetime(2025, 11, 10),
    datetime(2025, 11, 24),
    datetime(2025, 12, 8),
    datetime(2025, 12, 22),  # Q4 peak ~1M/week
    datetime(2026, 1, 5),
    datetime(2026, 1, 19),
    datetime(2026, 2, 2),
    datetime(2026, 2, 16),
    datetime(2026, 3, 2),    # Q1 2026 ~3.75M/week
]

weekly_txs = [
    200,
    1_500,
    8_000,
    35_000,
    85_000,
    156_492,
    320_000,
    550_000,
    780_000,
    1_000_000,
    1_400_000,
    1_900_000,
    2_500_000,
    3_100_000,
    3_750_000,
]

# Cumulative volume milestones (USD)
cum_dates = [
    datetime(2025, 10, 25),
    datetime(2025, 12, 22),
    datetime(2026, 3, 2),
]
cum_volume = [50_000_000, 600_000_000, 650_000_000]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Area chart
# ══════════════════════════════════════════════════
ax.fill_between(dates, weekly_txs, alpha=0.15, color='#0052ff')
ax.plot(dates, weekly_txs, color='#0052ff', linewidth=2.5, zorder=3)

# Highlight dots at key milestones
milestones = [
    (datetime(2025, 10, 25), 156_492, '156K'),
    (datetime(2025, 12, 22), 1_000_000, '1M'),
    (datetime(2026, 3, 2), 3_750_000, '3.75M'),
]
for d, v, label in milestones:
    ax.scatter([d], [v], color='#0052ff', s=50, zorder=5, edgecolors='white', linewidth=1.2)
    offset_y = v * 0.15
    ax.text(d, v + offset_y, label,
            ha='center', va='bottom',
            color=COLORS['text'], fontsize=11, fontweight='bold')

# ══════════════════════════════════════════════════
# Y-axis
# ══════════════════════════════════════════════════
ax.set_ylim(0, 4_500_000)
ax.set_yticks([0, 1_000_000, 2_000_000, 3_000_000, 4_000_000])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{x / 1_000_000:.0f}M' if x > 0 else '0'))
ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
               colors=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center', fontweight='bold')

ax.set_xlim(dates[0], dates[-1])

# ══════════════════════════════════════════════════
# Grid & spines
# ══════════════════════════════════════════════════
ax.grid(True, axis='y', color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'x402_weekly_transactions',
                                'outputs/charts/nanopayments')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
