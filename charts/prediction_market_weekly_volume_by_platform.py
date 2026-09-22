"""
Weekly Prediction Market Volume by Platform (week of 2026-08-24 ~ 08-30)

Data: hl.eco SSE feed `prediction-markets-volume` (platforms[].weekly, 마지막 완결 주),
      api.hl.eco/api/stream. Turnstile 세션이라 브라우저 컨텍스트에서만 열린다.
      스팟 거래대금, 완결 주만.
      단 Polymarket은 레퍼런스 값($1.92B, 15.4%) 유지. 피드가 이후 $1.96B로
      상향 리비전되면서 Kalshi 점유율도 82.1% -> 81.8%로 밀렸는데,
      레퍼런스 표기에 맞추기로 함. Field total $12.4B.
"""

import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import COLORS, DPI, FIGURE_SIZES, save_chart, setup_font

HIGHLIGHT = '#78DEC9'   # HIP-4
MUTED = '#4E525C'       # 나머지 플랫폼
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
colors = [HIGHLIGHT if p == 'HIP-4' else MUTED for p in df['platform']]
ax.barh(y, df['weekly_volume_usd'], height=0.62, color=colors, zorder=3)

ax.set_xscale('log')
ax.set_xlim(XMIN, 6e10)
ax.set_ylim(-0.7, len(df) - 0.3)

for yi, v, p in zip(y, df['weekly_volume_usd'], df['share_pct']):
    ax.text(v * 1.25, yi, f'{fmt_usd(v)}   {fmt_share(p)}', va='center',
            ha='left', color=COLORS['text'], fontsize=15, fontweight='bold')

ax.set_yticks(y, df['platform'])
ax.xaxis.set_major_locator(mticker.FixedLocator([1e6, 1e7, 1e8, 1e9, 1e10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_tick(v)))
ax.xaxis.set_minor_formatter(mticker.NullFormatter())

ax.spines['bottom'].set_color(COLORS['text_secondary'])
ax.spines['bottom'].set_linewidth(1.4)
for side in ('top', 'left', 'right'):
    ax.spines[side].set_visible(False)

ax.tick_params(axis='y', length=0, pad=12, labelsize=16, colors=COLORS['text'])
ax.tick_params(axis='x', which='major', length=6, width=1, pad=10,
               labelsize=15, colors=COLORS['text'])
ax.tick_params(axis='x', which='minor', length=0)
for lbl in ax.get_yticklabels() + ax.get_xticklabels():
    lbl.set_fontweight('bold')

fig.tight_layout()
png, svg = save_chart(fig, 'prediction_market_weekly_volume_by_platform',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
