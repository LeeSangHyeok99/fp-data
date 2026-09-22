"""
Weekly Prediction Market Volume by Platform, HRC dark theme.
데이터/구성은 charts/prediction_market_weekly_volume_by_platform.py와 동일, 팔레트만 HRC.
"""

import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI, FIGURE_SIZES, save_chart, setup_font
from hip4_hrc_palette import BODY, MUTED_BAR, OUTCOME, TITLE

XMIN = 1e6

df = pd.read_csv('outputs/data/prediction_market_weekly_volume_by_platform.csv')


def fmt_usd(v):
    return f'${v / 1e9:.1f}B' if v >= 1e9 else f'${v / 1e6:.1f}M'


def fmt_share(p):
    # 0.997처럼 반올림하면 1%가 되는 값은 1자리로 (레퍼런스 표기 1.0%)
    return f'{p:.1f}%' if round(p, 1) >= 1 else f'{p:.2f}%'


def fmt_tick(v):
    unit, div = ('B', 1e9) if v >= 1e9 else ('M', 1e6)
    return f'${v / div:g}{unit}'


setup_font()
fig, ax = plt.subplots(figsize=FIGURE_SIZES['horizontal_bar'], dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 큰 값이 위로 오도록 뒤집어 그린다
y = np.arange(len(df))[::-1]
colors = [OUTCOME if p == 'HIP-4' else MUTED_BAR for p in df['platform']]
ax.barh(y, df['weekly_volume_usd'], height=0.62, color=colors, zorder=3)

ax.set_xscale('log')
ax.set_xlim(XMIN, 6e10)
ax.set_ylim(-0.7, len(df) - 0.3)

for yi, v, p in zip(y, df['weekly_volume_usd'], df['share_pct']):
    ax.text(v * 1.25, yi, f'{fmt_usd(v)}   {fmt_share(p)}', va='center',
            ha='left', color=TITLE, fontsize=15, fontweight='bold')

ax.set_yticks(y, df['platform'])
ax.xaxis.set_major_locator(mticker.FixedLocator([1e6, 1e7, 1e8, 1e9, 1e10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_tick(v)))
ax.xaxis.set_minor_formatter(mticker.NullFormatter())

ax.spines['bottom'].set_color(BODY)
ax.spines['bottom'].set_linewidth(1.4)
for side in ('top', 'left', 'right'):
    ax.spines[side].set_visible(False)

ax.tick_params(axis='y', length=0, pad=12, labelsize=16, colors=TITLE)
ax.tick_params(axis='x', which='major', length=6, width=1, pad=10,
               labelsize=15, colors=BODY)
ax.tick_params(axis='x', which='minor', length=0)

fig.tight_layout()
png, svg = save_chart(fig, 'prediction_market_weekly_volume_by_platform_hrc',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
