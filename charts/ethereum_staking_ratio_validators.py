"""
Ethereum Staking Ratio vs Active Validators - Dual Y-axis Chart
Four Pillars design theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG, GRID_CONFIG

suit_path = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
if suit_path.exists():
    fm.fontManager.addfont(str(suit_path))
    suit_font = fm.FontProperties(fname=str(suit_path))
else:
    suit_font = None

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/ethereum_staking.csv')
df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y.%m')
df = df.sort_values('date').reset_index(drop=True)

dates = df['date']
ratio = df['staking_ratio_pct']
validators_m = df['validators_thousand'] / 1000.0  # millions

# ─── Colors ─────────────────────────────────────────────────────────────
BLUE = '#3B82F6'   # 스테이킹 비율
GREEN = '#22C55E'  # 활성 검증인 수

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('line')
fig.set_size_inches(15.0, 6.57)  # same ~2.285 ratio, scaled up
ax2 = ax.twinx()

# ─── Left axis: Staking ratio (area + line + dots) ─────────────────────
ax.fill_between(dates, ratio, 8, color=BLUE, alpha=0.18, linewidth=0, zorder=1)
ax.plot(dates, ratio, color=BLUE, linewidth=2.5, zorder=4)
ax.scatter(dates, ratio, color=BLUE, s=42, zorder=5, edgecolors='none')

# ─── Right axis: Active validators (dashed line + diamond) ─────────────
ax2.plot(dates, validators_m, color=GREEN, linewidth=2.2,
         linestyle=(0, (6, 4)), zorder=3)
ax2.scatter(dates, validators_m, color=GREEN, marker='D', s=44,
            zorder=5, edgecolors='none')

# ─── Y axes (5 aligned ticks each) ─────────────────────────────────────
ax.set_ylim(8, 32)
left_ticks = [10, 15, 20, 25, 30]
ax.set_yticks(left_ticks)
Y_TICK_SIZE = 28
X_TICK_SIZE = 17
ax.set_yticklabels(
    [f'{v}%' for v in left_ticks],
    fontsize=Y_TICK_SIZE,
    fontweight='bold',
    color=BLUE,
    fontproperties=suit_font,
)

ax2.set_ylim(0.32, 1.28)
right_ticks = [0.4, 0.6, 0.8, 1.0, 1.2]
ax2.set_yticks(right_ticks)
right_font = fm.FontProperties(fname=str(suit_path), size=Y_TICK_SIZE) if suit_path.exists() else None
ax2.set_yticklabels(
    [f'{v:.1f}M' for v in right_ticks],
    fontsize=Y_TICK_SIZE,
    fontweight='bold',
    color=GREEN,
    fontproperties=right_font,
)
ax2.tick_params(axis='y', labelsize=Y_TICK_SIZE)

# ─── X axis: Mon YYYY format, all data points ──────────────────────────
import matplotlib.ticker as mticker
ax.xaxis.set_major_locator(mticker.FixedLocator(mdates.date2num(dates)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
x_font = fm.FontProperties(fname=str(suit_path), size=X_TICK_SIZE) if suit_path.exists() else None
for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(X_TICK_SIZE)
    label.set_fontweight('bold')
    label.set_color(AXIS_CONFIG['x_tick']['color'])
    label.set_rotation(45)
    label.set_ha('right')
    if x_font:
        label.set_fontproperties(x_font)

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'line')

# apply_style overrides x labelsize, re-apply our smaller size
ax.tick_params(axis='x', labelsize=X_TICK_SIZE)
for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(X_TICK_SIZE)
    if x_font:
        label.set_fontproperties(x_font)

# Right axis cosmetic: hide spine, no tick marks, grid off
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', length=0, pad=15)
ax2.grid(False)

# Left axis tick marks off (grid only) + restore blue color + size
ax.tick_params(axis='y', length=0, colors=BLUE, labelsize=Y_TICK_SIZE)
ax.tick_params(axis='x', length=0)
for label in ax.yaxis.get_majorticklabels():
    label.set_color(BLUE)
    label.set_fontsize(Y_TICK_SIZE)

ax.set_xlim(dates.min() - pd.Timedelta(days=25), dates.max() + pd.Timedelta(days=25))

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/ethereum/staking'
png_path, svg_path = save_chart(fig, 'ethereum_staking_ratio_validators', output_dir)
plt.close()

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
