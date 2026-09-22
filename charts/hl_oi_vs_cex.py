import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, '.claude/skills/design/hrc')
from config import (setup_font, COLORS, GRID_CONFIG, AXIS_CONFIG, DPI, DEFAULT_FIGSIZE)

setup_font()

output_dir = 'outputs/charts/hyperliquid/oi'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/hypeflows_oi_ratio.csv', parse_dates=['date'])
df = df.sort_values('date')

# Market Share = HL / (HL + CEX) * 100 (matching hypeflows "Custom" chart)
df['hl_bn_share'] = df['hyperliquid_oi'] / (df['hyperliquid_oi'] + df['binance_oi']) * 100
df['hl_bybit_share'] = df['hyperliquid_oi'] / (df['hyperliquid_oi'] + df['bybit_oi']) * 100
df['hl_okx_share'] = df['hyperliquid_oi'] / (df['hyperliquid_oi'] + df['okx_oi']) * 100

# 14D rolling average
df['hl_bn_14d'] = df['hl_bn_share'].rolling(14, min_periods=1).mean()
df['hl_bybit_14d'] = df['hl_bybit_share'].rolling(14, min_periods=1).mean()
df['hl_okx_14d'] = df['hl_okx_share'].rolling(14, min_periods=1).mean()

# =============================================================================
# Chart: HL OI as % of each CEX (multi-line, 14D rolling avg)
# =============================================================================
fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE, dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Lines
ax.plot(df['date'], df['hl_bn_14d'], color='#5470c6', linewidth=2.2, zorder=3)
ax.plot(df['date'], df['hl_bybit_14d'], color='#ee6666', linewidth=2.2, zorder=3)
ax.plot(df['date'], df['hl_okx_14d'], color='#3ba272', linewidth=2.2, zorder=3)

# Endpoint labels
for col, color, label in [
    ('hl_bn_14d', '#5470c6', 'Binance'),
    ('hl_bybit_14d', '#ee6666', 'Bybit'),
    ('hl_okx_14d', '#3ba272', 'OKX'),
]:
    last_val = df[col].iloc[-1]
    ax.text(df['date'].iloc[-1] + pd.Timedelta(days=2), last_val,
            f'{last_val:.1f}%',
            color=color, fontsize=14, fontweight='bold', va='center')

# Y axis
y_ticks = [10, 20, 30, 40]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold',
                    color=AXIS_CONFIG['y_tick']['color'])
ax.set_ylim(8, 42)

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'],
               pad=AXIS_CONFIG['x_tick']['pad'],
               colors=AXIS_CONFIG['x_tick']['color'])

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', length=0, pad=15)

# Margins
ax.margins(x=0.02)

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hl_oi_vs_cex.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print(f'Latest HL/Binance: {df["hl_bn_14d"].iloc[-1]:.1f}%')
print(f'Latest HL/Bybit: {df["hl_bybit_14d"].iloc[-1]:.1f}%')
print(f'Latest HL/OKX: {df["hl_okx_14d"].iloc[-1]:.1f}%')
print(f'Date range: {df["date"].iloc[0].strftime("%Y-%m-%d")} ~ {df["date"].iloc[-1].strftime("%Y-%m-%d")}')
print(f'\nDone: hl_oi_vs_cex (png + svg)')
