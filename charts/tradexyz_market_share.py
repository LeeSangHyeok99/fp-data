import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import endpoint_dot
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/tradexyz'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('data/dune_hip3_builder_volume_daily.csv', parse_dates=['day'])

# Drop last row if it's a partial day (very low volume)
if df.iloc[-1]['hl_core'] < 500_000_000:
    df = df.iloc[:-1]

# Total volume per day
builders = ['tradexyz', 'felix', 'dreamcash', 'hyena', 'markets', 'ventuals']
df['total'] = df['hl_core'] + df[builders].sum(axis=1)
df['hip3_total'] = df[builders].sum(axis=1)

# Market share (% of total Hyperliquid volume)
for b in builders:
    df[f'{b}_share'] = df[b] / df['total'] * 100
df['hip3_share'] = df['hip3_total'] / df['total'] * 100

# 7-day rolling for smoother chart
for b in builders + ['hip3']:
    df[f'{b}_share_7d'] = df[f'{b}_share'].rolling(7, min_periods=1).mean()

# =============================================================================
# Chart: TradeXYZ Market Share of Hyperliquid Volume (7d MA)
# =============================================================================
setup_font()

TXYZ_COLOR = '#f97316'
HIP3_COLOR = '#f97316'  # lighter for other HIP-3
HL_CORE_COLOR = '#50e3c2'

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Stacked areas: TradeXYZ share + other HIP-3 builders share
other_hip3_share = df['hip3_share_7d'] - df['tradexyz_share_7d']

# Fill: other HIP-3 builders (lighter)
ax.fill_between(df['day'], df['tradexyz_share_7d'], df['hip3_share_7d'],
                color='#fb923c', alpha=0.3, zorder=2)

# Fill: TradeXYZ
ax.fill_between(df['day'], 0, df['tradexyz_share_7d'],
                color=TXYZ_COLOR, alpha=0.5, zorder=3)

# Lines
ax.plot(df['day'], df['hip3_share_7d'], color='#fb923c', linewidth=1.5,
        alpha=0.6, zorder=4)
ax.plot(df['day'], df['tradexyz_share_7d'], color=TXYZ_COLOR, linewidth=2.5,
        zorder=5)

# Endpoint dots and labels
last = df.iloc[-1]
endpoint_dot(ax, last['day'], last['tradexyz_share_7d'], TXYZ_COLOR, size=60)
endpoint_dot(ax, last['day'], last['hip3_share_7d'], '#fb923c', size=40)

ax.annotate(
    f'TradeXYZ {last["tradexyz_share_7d"]:.0f}%',
    xy=(last['day'], last['tradexyz_share_7d']),
    xytext=(8, -5),
    textcoords='offset points',
    ha='left', va='top',
    fontsize=14, fontweight='bold',
    color=TXYZ_COLOR,
)

ax.annotate(
    f'All HIP-3 {last["hip3_share_7d"]:.0f}%',
    xy=(last['day'], last['hip3_share_7d']),
    xytext=(8, 5),
    textcoords='offset points',
    ha='left', va='bottom',
    fontsize=12, fontweight='bold',
    color='#fb923c',
)

# Key event: S&P 500 License
sp500_date = pd.Timestamp('2026-03-18')
if sp500_date >= df['day'].min():
    ax.axvline(sp500_date, color=COLORS['text_secondary'], alpha=0.4,
               linestyle='--', linewidth=1, zorder=1)
    ax.annotate(
        'S&P 500\nLicense',
        xy=(sp500_date, 35),
        xytext=(-45, 8),
        textcoords='offset points',
        ha='center', va='bottom',
        fontsize=11, fontweight='bold',
        color=COLORS['text'],
        arrowprops=dict(arrowstyle='->', color=COLORS['text_secondary'], lw=1.2),
    )

# Iran oil crisis annotation
iran_date = pd.Timestamp('2026-03-09')
if iran_date >= df['day'].min():
    ax.axvline(iran_date, color=COLORS['text_secondary'], alpha=0.4,
               linestyle='--', linewidth=1, zorder=1)
    ax.annotate(
        'Iran Crisis\nWeekend',
        xy=(iran_date, 30),
        xytext=(-45, 8),
        textcoords='offset points',
        ha='center', va='bottom',
        fontsize=11, fontweight='bold',
        color=COLORS['text'],
        arrowprops=dict(arrowstyle='->', color=COLORS['text_secondary'], lw=1.2),
    )

# Y axis
y_ticks = np.arange(0, 50, 10)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{int(v)}%' for v in y_ticks],
                    fontsize=18, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 48)

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax.xaxis.get_majorticklabels(),
         fontsize=16, fontweight='bold',
         color=COLORS['text_secondary'],
         rotation=45, ha='right')

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0)

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/tradexyz_volume_share.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Stats
# =============================================================================
print('=== TradeXYZ Volume Market Share ===')
print(f'Latest 7d avg: {last["tradexyz_share_7d"]:.1f}%')
print(f'Peak (7d avg): {df["tradexyz_share_7d"].max():.1f}% on {df.loc[df["tradexyz_share_7d"].idxmax(), "day"].strftime("%Y-%m-%d")}')
print(f'Peak (daily): {df["tradexyz_share"].max():.1f}% on {df.loc[df["tradexyz_share"].idxmax(), "day"].strftime("%Y-%m-%d")}')
print(f'\nAll HIP-3 latest 7d avg: {last["hip3_share_7d"]:.1f}%')
print(f'All HIP-3 peak (7d avg): {df["hip3_share_7d"].max():.1f}%')
print(f'\nPeak daily TradeXYZ volume: ${df["tradexyz"].max()/1e9:.2f}B on {df.loc[df["tradexyz"].idxmax(), "day"].strftime("%Y-%m-%d")}')
print(f'\nDone: tradexyz_volume_share.png')
