import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import area_glow, endpoint_dot
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/tradexyz'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
txyz = pd.read_csv('outputs/data/tradexyz_daily_fees.csv', parse_dates=['date'])
hl = pd.read_csv('outputs/data/hyperliquid_daily_fees.csv', parse_dates=['date'])

# Merge on date
df = pd.merge(txyz, hl, on='date', suffixes=('_txyz', '_hl'))

# 7-day rolling averages for smoother visualization
df['txyz_7d'] = df['fees_usd_txyz'].rolling(7, min_periods=1).mean()
df['hl_7d'] = df['fees_usd_hl'].rolling(7, min_periods=1).mean()
df['share_7d'] = df['txyz_7d'] / df['hl_7d'] * 100

# =============================================================================
# Chart: TradeXYZ Fee Share of Hyperliquid (7d MA)
# =============================================================================
setup_font()

TXYZ_COLOR = '#f97316'  # TradeXYZ orange
HL_COLOR = '#50e3c2'    # Hyperliquid teal

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Area glow for fee share
area_glow(ax, df['date'], df['share_7d'], color=TXYZ_COLOR, max_alpha=0.22, power=2.0)

# Main line
ax.plot(df['date'], df['share_7d'], color=TXYZ_COLOR, linewidth=2.5, zorder=4)

# Endpoint dot
endpoint_dot(ax, df['date'].iloc[-1], df['share_7d'].iloc[-1], color=TXYZ_COLOR, size=60)

# Endpoint label
last_val = df['share_7d'].iloc[-1]
ax.annotate(
    f'{last_val:.1f}%',
    xy=(df['date'].iloc[-1], last_val),
    xytext=(8, 0),
    textcoords='offset points',
    ha='left', va='center',
    fontsize=16, fontweight='bold',
    color=TXYZ_COLOR,
)

# Key event annotations
# S&P 500 License: March 18, 2026
sp500_date = pd.Timestamp('2026-03-18')
if sp500_date in df['date'].values:
    sp500_share = df.loc[df['date'] == sp500_date, 'share_7d'].values[0]
    ax.axvline(sp500_date, color=COLORS['text_secondary'], alpha=0.4,
               linestyle='--', linewidth=1, zorder=1)
    ax.annotate(
        'S&P 500\nLicense',
        xy=(sp500_date, sp500_share),
        xytext=(-50, 30),
        textcoords='offset points',
        ha='center', va='bottom',
        fontsize=11, fontweight='bold',
        color=COLORS['text'],
        arrowprops=dict(arrowstyle='->', color=COLORS['text_secondary'], lw=1.2),
    )

# Y axis
y_max_raw = df['share_7d'].max()
y_max = np.ceil(y_max_raw / 5) * 5
if y_max < 20:
    y_max = 20
y_ticks = np.arange(0, y_max + 5, 5)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{int(v)}%' for v in y_ticks],
                    fontsize=18, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, y_max + 2)

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

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/tradexyz_fee_share.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()

# =============================================================================
# Chart 2: Dual - TradeXYZ 7d fees vs Hyperliquid 7d fees (stacked area)
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig2.patch.set_alpha(0)
ax2.set_facecolor('none')

# Convert to millions
df['txyz_7d_m'] = df['txyz_7d'] / 1e6
df['hl_only_7d_m'] = (df['hl_7d'] - df['txyz_7d']) / 1e6  # HL native (excl TradeXYZ)

# Stacked area
ax2.fill_between(df['date'], 0, df['txyz_7d_m'],
                 color=TXYZ_COLOR, alpha=0.8, label='TradeXYZ', zorder=3)
ax2.fill_between(df['date'], df['txyz_7d_m'], df['txyz_7d_m'] + df['hl_only_7d_m'],
                 color=HL_COLOR, alpha=0.6, label='Hyperliquid Native', zorder=2)

# Endpoint labels
last_txyz = df['txyz_7d_m'].iloc[-1]
last_hl = df['hl_only_7d_m'].iloc[-1]
last_total = last_txyz + last_hl

ax2.annotate(
    f'${last_txyz:.2f}M',
    xy=(df['date'].iloc[-1], last_txyz / 2),
    xytext=(8, 0),
    textcoords='offset points',
    ha='left', va='center',
    fontsize=13, fontweight='bold',
    color=TXYZ_COLOR,
)

ax2.annotate(
    f'${last_total:.1f}M',
    xy=(df['date'].iloc[-1], last_total),
    xytext=(8, 0),
    textcoords='offset points',
    ha='left', va='center',
    fontsize=13, fontweight='bold',
    color=HL_COLOR,
)

# Y axis
y_max_raw2 = (df['txyz_7d_m'] + df['hl_only_7d_m']).max()
y_max2 = np.ceil(y_max_raw2 / 1) * 1
if y_max2 < 5:
    y_ticks2 = np.arange(0, y_max2 + 1, 1)
elif y_max2 < 10:
    y_ticks2 = np.arange(0, y_max2 + 2, 2)
else:
    step = np.ceil(y_max2 / 5)
    y_ticks2 = np.arange(0, y_max2 + step, step)

ax2.set_yticks(y_ticks2)
ax2.set_yticklabels([f'${v:.0f}M' if v >= 1 else f'${v:.1f}M' for v in y_ticks2],
                     fontsize=18, fontweight='bold',
                     color=COLORS['text_secondary'])
ax2.set_ylim(0, y_max2 * 1.1)

# X axis
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax2.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax2.xaxis.get_majorticklabels(),
         fontsize=16, fontweight='bold',
         color=COLORS['text_secondary'],
         rotation=45, ha='right')

# Grid
ax2.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax2.set_axisbelow(True)

for spine in ax2.spines.values():
    spine.set_visible(False)

ax2.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])
ax2.tick_params(axis='y', length=0)

fig2.tight_layout()

for fmt in ['png', 'svg']:
    fig2.savefig(
        f'{output_dir}/tradexyz_vs_hl_fees.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()

# =============================================================================
# Stats
# =============================================================================
print('=== Chart 1: TradeXYZ Fee Share ===')
print(f'Latest 7d avg share: {last_val:.1f}%')
print(f'Peak share: {df["share_7d"].max():.1f}% on {df.loc[df["share_7d"].idxmax(), "date"].strftime("%Y-%m-%d")}')
print(f'Min share: {df["share_7d"].min():.1f}%')
print()
print('=== Chart 2: Fee Comparison ===')
print(f'TradeXYZ total fees: ${txyz["fees_usd"].sum()/1e6:.1f}M')
print(f'Hyperliquid total fees (overlap): ${df["fees_usd_hl"].sum()/1e6:.1f}M')
print(f'Latest 7d: TradeXYZ ${last_txyz:.2f}M/day vs HL ${last_total:.1f}M/day total')
print()
print('Done: tradexyz_fee_share.png / tradexyz_vs_hl_fees.png')
