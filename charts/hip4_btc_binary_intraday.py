"""
HIP-4 BTC Daily Binary: Intraday YES probability vs BTC perp
Window: 2026-05-05 06:00 UTC -> 2026-05-06 02:00 UTC (21h, current cycle)
Target: $80,930 (settles 2026-05-06 06:00 UTC)
Source: Hyperliquid info API (candleSnapshot)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import COLORS, GRID_CONFIG, AXIS_CONFIG, DPI

font_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
else:
    plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.weight'] = 'bold'

BTC_COLOR = '#f7931a'
YES_COLOR = '#26a69a'
TARGET_COLOR = '#787b86'

df = pd.read_csv('outputs/data/hip4_btc_binary_hourly.csv')
df['ts'] = pd.to_datetime(df['timestamp_utc'])

target_price = 80930

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10.67, 5.6), dpi=DPI,
    sharex=True, gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.18}
)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')
ax2.set_facecolor('none')

# ── Top: BTC price ─────────────────────────────────────────────
ax1.plot(df['ts'], df['btc_close'], color=BTC_COLOR, linewidth=2.4, zorder=3)
ax1.fill_between(df['ts'], df['btc_close'], target_price,
                 where=(df['btc_close'] >= target_price),
                 color=BTC_COLOR, alpha=0.12, zorder=1)

ax1.axhline(target_price, color=TARGET_COLOR, linewidth=1.2,
            linestyle=(0, (4, 3)), alpha=0.9, zorder=2)
ax1.text(df['ts'].iloc[0], target_price, '  Target $80,930',
         color=TARGET_COLOR, fontsize=11, fontweight='bold',
         va='bottom', ha='left')

ax1.set_ylim(80400, 81800)
ax1.set_yticks([80500, 81000, 81500])
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v/1000:.1f}K'))

# ── Bottom: YES probability ────────────────────────────────────
ax2.fill_between(df['ts'], df['yes_close'], 0,
                 color=YES_COLOR, alpha=0.18, zorder=1)
ax2.plot(df['ts'], df['yes_close'], color=YES_COLOR, linewidth=2.4, zorder=3)

ax2.set_ylim(0.40, 0.90)
ax2.set_yticks([0.40, 0.60, 0.80])
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v*100:.0f}%'))

# ── Shared X axis ──────────────────────────────────────────────
ax2.xaxis.set_major_locator(mdates.HourLocator(byhour=[6, 12, 18, 0]))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))

for ax in (ax1, ax2):
    ax.grid(True, axis='y',
            color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='y',
                   labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 4,
                   pad=AXIS_CONFIG['y_tick']['pad'] - 5,
                   length=0,
                   colors=AXIS_CONFIG['y_tick']['color'])

ax2.tick_params(axis='x',
                labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 3,
                pad=AXIS_CONFIG['x_tick']['pad'],
                length=0,
                colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax2.xaxis.get_majorticklabels(), ha='center', rotation=0)
ax1.tick_params(axis='x', length=0)

# Endpoint dots
ax1.scatter(df['ts'].iloc[-1], df['btc_close'].iloc[-1],
            color=BTC_COLOR, s=42, zorder=5, edgecolor='none')
ax2.scatter(df['ts'].iloc[-1], df['yes_close'].iloc[-1],
            color=YES_COLOR, s=42, zorder=5, edgecolor='none')

fig.tight_layout()

out_dir = Path('outputs/charts/hyperliquid/hip4')
out_dir.mkdir(parents=True, exist_ok=True)
fname = 'hip4_btc_binary_intraday'
fig.savefig(out_dir / f'{fname}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(out_dir / f'{fname}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)

print(f'Saved: {out_dir/fname}.png')
print(f'Saved: {out_dir/fname}.svg')
print(f'BTC range: ${df["btc_close"].min():,.0f} - ${df["btc_close"].max():,.0f}')
print(f'YES prob range: {df["yes_close"].min():.3f} - {df["yes_close"].max():.3f}')
print(f'Total volume: {df["volume_contracts"].sum():,.0f} contracts')
print(f'Total trades: {df["trades"].sum():,}')
plt.close(fig)
