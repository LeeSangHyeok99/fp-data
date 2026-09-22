import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

import importlib.util
_spec = importlib.util.spec_from_file_location('fp_config', '.claude/skills/design/four-pillars/config.py')
_fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fp)
endpoint_dot = _fp.endpoint_dot

output_dir = 'outputs/charts/hyperliquid/metrics'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/hypeflows_perp_volume.csv', parse_dates=['date'])

# Hypeflows Market Share formula: HL_14d_sum / (HL_14d_sum + CEX_14d_sum) * 100
# Sum volumes over 14d window first, THEN compute ratio
hl_14d = df['hyperliquid'].rolling(14, min_periods=7).sum()
bn_14d = df['binance'].rolling(14, min_periods=7).sum()
bb_14d = df['bybit'].rolling(14, min_periods=7).sum()
ok_14d = df['okx'].rolling(14, min_periods=7).sum()

df['hl_vs_binance_14d'] = hl_14d / (hl_14d + bn_14d) * 100
df['hl_vs_bybit_14d'] = hl_14d / (hl_14d + bb_14d) * 100
df['hl_vs_okx_14d'] = hl_14d / (hl_14d + ok_14d) * 100

# Clean
for col in [c for c in df.columns if '14d' in c]:
    df[col] = df[col].replace([np.inf, -np.inf], np.nan)

# =============================================================================
# Chart: HL vs CEX Perp Volume Ratio (14d Rolling Avg)
# =============================================================================
setup_font()

COLOR_BINANCE = '#F0B90B'
COLOR_BYBIT = '#ee6666'
COLOR_OKX = '#10b981'

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Lines
ax.plot(df['date'], df['hl_vs_bybit_14d'], color=COLOR_BYBIT, linewidth=2.5, zorder=5)
ax.plot(df['date'], df['hl_vs_okx_14d'], color=COLOR_OKX, linewidth=2.5, zorder=4)
ax.plot(df['date'], df['hl_vs_binance_14d'], color=COLOR_BINANCE, linewidth=2.5, zorder=3)

# Endpoint dots
last = df.dropna(subset=['hl_vs_binance_14d']).iloc[-1]
for col, color in [('hl_vs_bybit_14d', COLOR_BYBIT), ('hl_vs_okx_14d', COLOR_OKX), ('hl_vs_binance_14d', COLOR_BINANCE)]:
    if not pd.isna(last[col]):
        endpoint_dot(ax, last['date'], last[col], color, size=50)

# Y axis
y_max = df[['hl_vs_bybit_14d', 'hl_vs_okx_14d']].max().max()
y_ceil = np.ceil(y_max / 10) * 10
y_ticks = np.arange(0, y_ceil + 10, 10)
if len(y_ticks) > 6:
    y_ticks = np.arange(0, y_ceil + 10, 20)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{int(v)}%' if v > 0 else '' for v in y_ticks],
                    fontsize=16, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, y_ceil + 5)

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.tick_params(axis='x', labelsize=14, length=6, width=1,
               colors=COLORS['text_secondary'])
fig.autofmt_xdate(rotation=45, ha='right')
for label in ax.xaxis.get_majorticklabels():
    label.set_fontweight('bold')
    label.set_color(COLORS['text_secondary'])

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', length=0)

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hl_vs_cex_volume_ratio.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Stats
# =============================================================================
print('=== HL vs CEX Perp Volume Ratio (14d avg, latest) ===')
print(f'vs Binance: {last["hl_vs_binance_14d"]:.1f}%')
print(f'vs Bybit: {last["hl_vs_bybit_14d"]:.1f}%')
print(f'vs OKX: {last["hl_vs_okx_14d"]:.1f}%')

# 6 months ago
first_valid = df.dropna(subset=['hl_vs_binance_14d']).iloc[0]
print(f'\n6 months ago ({first_valid["date"].strftime("%Y-%m-%d")}):')
print(f'vs Binance: {first_valid["hl_vs_binance_14d"]:.1f}%')
print(f'vs Bybit: {first_valid["hl_vs_bybit_14d"]:.1f}%')
print(f'vs OKX: {first_valid["hl_vs_okx_14d"]:.1f}%')

print(f'\nDone: hl_vs_cex_volume_ratio.png')
