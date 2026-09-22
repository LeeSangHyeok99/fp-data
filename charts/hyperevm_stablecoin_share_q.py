"""
HyperEVM Stablecoin Supply Share (100% stacked area) — four-pillars theme
Quarterly view: 2026-01-23 to 2026-04-24
Data: ASXN api-hyperliquid.asxn.xyz /api/hyper-evm/stablecoin-supply-chart
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
from pathlib import Path
from config import create_figure, apply_style, save_chart, AXIS_CONFIG

pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
kr_font = None
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    kr_font = fm.FontProperties(fname=str(pretendard_path))

df = pd.read_csv('outputs/data/asxn_stablecoin_supply_2026_04_24.csv')
df['date'] = pd.to_datetime(df['date'])
df = df[(df['date'] >= '2026-01-23') & (df['date'] <= '2026-04-24')].reset_index(drop=True)

stack_order = ['USDC', 'USDT0', 'USDH', 'USDe', 'feUSD', 'thBILL', 'USDXL', 'USDHL', 'USH', 'USR']
color_map = {
    'USDC':   '#2775ca',
    'USDT0':  '#26a17b',
    'USDH':   '#50e3c2',
    'USDe':   '#b8b8d1',
    'feUSD':  '#7ee8b8',
    'thBILL': '#fac858',
    'USDXL':  '#9a60b4',
    'USDHL':  '#1e4a3a',
    'USH':    '#5470c6',
    'USR':    '#787b86',
}

pct = df[stack_order].div(df[stack_order].sum(axis=1), axis=0) * 100
dates = df['date']

fig, ax = create_figure('stacked')

ax.stackplot(
    dates,
    [pct[tok].values for tok in stack_order],
    colors=[color_map[tok] for tok in stack_order],
    alpha=0.95,
    edgecolor='none',
    linewidth=0,
)

ax.set_xlim(dates.min(), dates.max())
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'],
                   fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                   fontweight='bold',
                   color=AXIS_CONFIG['y_tick']['color'],
                   fontproperties=kr_font)

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
def xfmt(val, pos):
    return mdates.num2date(val).strftime('%b %Y')
ax.xaxis.set_major_formatter(FuncFormatter(xfmt))

for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(AXIS_CONFIG['x_tick']['fontsize'])
    label.set_fontweight('bold')
    label.set_color(AXIS_CONFIG['x_tick']['color'])
    label.set_rotation(45)
    label.set_ha('right')
    if kr_font:
        label.set_fontproperties(kr_font)

apply_style(fig, ax, 'stacked')
ax.tick_params(axis='x', length=0)
ax.tick_params(axis='y', pad=5)

output_dir = 'outputs/charts/hyperliquid/stablecoin'
png_path, svg_path = save_chart(fig, 'hyperevm_stablecoin_share_q', output_dir)
plt.close()

print(f"Saved: {png_path}")
print(f"Rows: {len(df)}  {dates.min().date()} → {dates.max().date()}")
print(f"Latest USDC%: {pct['USDC'].iloc[-1]:.1f}%  USDT0%: {pct['USDT0'].iloc[-1]:.1f}%  USDH%: {pct['USDH'].iloc[-1]:.1f}%")
