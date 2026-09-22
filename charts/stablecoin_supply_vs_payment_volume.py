"""Stablecoin total value vs. stablecoin payment volume (last 12 months).

Merged dual-axis chart:
  line (right, $B) = total stablecoin market cap, month-end
  stacked bars (left, $M) = monthly onchain card payment volume,
                            top 4 projects + Others

Data: outputs/data/stablecoin_supply_vs_payment_volume.csv
  mcap   = sources/rwa-xyz-stablecoin-market-caps.csv (123 tokens summed)
  volume = research.4pillars.io/en/data/payment (live, 2026-09-01)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, gradient_rounded_bar

setup_font()

df = pd.read_csv('outputs/data/stablecoin_supply_vs_payment_volume.csv')
months = pd.to_datetime(df['month'] + '-01')
n = len(df)
x = np.arange(n, dtype=float)

# line: daily total stablecoin market cap over the same 12-month window,
# straight from the rwa.xyz export. x maps each day onto its month's bar
# (bar center = mid-month), so the line rides the bars month for month.
sc = pd.read_csv('sources/rwa-xyz-stablecoin-market-caps.csv')
sc['Date'] = pd.to_datetime(sc['Date'])
sc = sc[(sc['Date'] >= months[0]) &
        (sc['Date'] < months.iloc[-1] + pd.offsets.MonthBegin(1))]
mcap = sc.drop(columns=['Timestamp', 'Date', 'Measure']).apply(
    pd.to_numeric, errors='coerce').sum(axis=1) / 1e9              # $B
# 7d centered mean: keeps the shape, drops the daily jitter
mcap = mcap.rolling(7, center=True, min_periods=1).mean().to_numpy()
mi = (sc['Date'].dt.year - months[0].year) * 12 + sc['Date'].dt.month - months[0].month
day_frac = (sc['Date'].dt.day - 1) / sc['Date'].dt.days_in_month
mcap_x = (mi + day_frac - 0.5).to_numpy()

# stack order bottom -> top (largest first)
PROJECTS = [
    ('RedotPay',    '#ca5532'),
    ('Other Rain',  '#4092c3'),
    ('Other Wirex', '#c39040'),
    ('EtherFi',     '#9231ab'),
    ('Others',      '#787878'),
]
LINE_COLOR = '#f2f2f2'
BAR_AXIS_COLOR = '#e8623a'

OUTPUT_DIR = Path('outputs/charts/stablecoin/payment')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2 = ax.twinx()
ax2.set_facecolor('none')

# axis ranges up front: gradient_rounded_bar needs final limits
ax.set_ylim(0, 1320)
ax.set_xlim(-0.7, n - 0.3)

# bars: payment volume (left, $M), per-segment vertical gradient, flat tops
bottom = np.zeros(n)
for name, color in PROJECTS:
    vals = df[name].to_numpy() / 1e6
    for xc, v, y0 in zip(x, vals, bottom):
        gradient_rounded_bar(ax, xc, 0.62, y0 + v, color, floor=0.68,
                             round_top=False, y0=y0)
    bottom += vals

# line: stablecoin market cap (right, $B)
ax2.plot(mcap_x, mcap, color=LINE_COLOR, linewidth=2.6, zorder=5,
         solid_capstyle='round', solid_joinstyle='round')
ax2.scatter(mcap_x[-1], mcap[-1], color=LINE_COLOR, s=42, zorder=6, edgecolors='none')

# both axes: 5 ticks on the same gridlines (0 / .227 / .455 / .682 / .909).
# scaled so the line runs through the top of the bars instead of floating above.
left_ticks = [0, 300, 600, 900, 1200]
ax.set_yticks(left_ticks)
ax.set_yticklabels([f'${t:,}M' for t in left_ticks], fontsize=16,
                   fontweight='bold', color=BAR_AXIS_COLOR)

right_ticks = [0, 100, 200, 300, 400]
ax2.set_yticks(right_ticks)
ax2.set_yticklabels([f'${t}B' for t in right_ticks], fontsize=15,
                    fontweight='bold', color=LINE_COLOR)
ax2.set_ylim(0, 440)

ax.set_xticks(range(n))
ax.set_xticklabels([m.strftime('%b %Y') for m in months], fontsize=12,
                   fontweight='bold', color=COLORS['text'])
ax.tick_params(axis='x', rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in list(ax.spines.values()) + list(ax2.spines.values()):
    spine.set_visible(False)
ax.tick_params(axis='y', length=0)
ax2.tick_params(axis='y', length=0, pad=3)
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(OUTPUT_DIR / f'stablecoin_supply_vs_payment_volume_wide.{fmt}',
                dpi=DPI, facecolor='none', edgecolor='none',
                bbox_inches='tight', transparent=True)
plt.close(fig)

print(f'{df["month"].iloc[0]} ~ {df["month"].iloc[-1]}')
print(f'  mcap   ${mcap[0]:.1f}B -> ${mcap[-1]:.1f}B ({mcap[-1]/mcap[0]-1:+.1%})')
print(f'  volume ${bottom[0]:.0f}M -> ${bottom[-1]:.0f}M ({bottom[-1]/bottom[0]-1:+.1%})')
