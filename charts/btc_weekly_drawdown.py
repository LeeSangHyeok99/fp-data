"""
BTC Weekly Candlestick with Drawdown Annotation
레퍼런스(TradingView 측정도구) 내재화: 2025-10 peak -> 2026-06 trough
-60,644.59 (-48.95%), 35 bars, 245d
four-pillars dark theme.
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, POSITIVE_COLOR, NEGATIVE_COLOR, save_chart  # noqa: E402

setup_font()

BG = COLORS['background']          # #141414
UP = POSITIVE_COLOR                # #26a69a
DOWN = NEGATIVE_COLOR             # #ef5350
TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']

# 레퍼런스 측정도구 수치
PEAK_LEVEL = 123902.84
LAST_LEVEL = 63258.24
DD_ABS = LAST_LEVEL - PEAK_LEVEL           # -60,644.60
DD_PCT = DD_ABS / PEAK_LEVEL * 100         # -48.95%

# ---------------------------------------------------------------- data
df = pd.read_csv('outputs/data/btc_weekly_drawdown.csv', parse_dates=['date'])
df = df.reset_index(drop=True)
x = np.arange(len(df))

PEAK_DATE = pd.Timestamp('2025-10-06')
peak_i = int(df.index[df['date'] == PEAK_DATE][0])
last_i = len(df) - 1

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax = fig.add_subplot(111)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

# ---------------------------------------------------------------- candles
W = 0.62
for i, row in df.iterrows():
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    col = UP if c >= o else DOWN
    ax.vlines(i, l, h, color=col, linewidth=1.1, zorder=3)
    lo, hi = min(o, c), max(o, c)
    ax.add_patch(plt.Rectangle((i - W / 2, lo), W, max(hi - lo, 1),
                               facecolor=col, edgecolor=col, linewidth=0.5, zorder=4))

# y축 범위 (박스가 차트 상단까지 닿도록 먼저 정의)
y_bottom = df['low'].min() * 0.92
y_top = df['high'].max() * 1.03

# ---------------------------------------------------------------- drawdown box
box_x0, box_x1 = peak_i - 0.3, last_i + 0.4
box_top = y_top        # 차트 젤 위
box_bottom = 60000     # $60K 라인
ax.add_patch(plt.Rectangle((box_x0, box_bottom), box_x1 - box_x0, box_top - box_bottom,
                           facecolor=DOWN, alpha=0.10, edgecolor='none', zorder=2))
# 박스 테두리
ax.hlines(box_top, box_x0, box_x1, color=DOWN, linewidth=1.0, alpha=0.45, zorder=2)
ax.hlines(box_bottom, box_x0, box_x1, color=DOWN, linewidth=1.0,
          linestyle=(0, (2, 2)), alpha=0.7, zorder=2)
# 시작점 수직 기준선
ax.vlines(peak_i, box_bottom, box_top, color=DOWN, linewidth=1.0, alpha=0.4, zorder=2)

# ---------------------------------------------------------------- annotation label
mid_x = (box_x0 + box_x1) / 2
# 레퍼런스 측정도구 표기 그대로 (-60,644.59)
label = "-60,644.59 (-48.95%)\n35 bars,  245d"
ax.annotate(
    label, xy=(mid_x, LAST_LEVEL), xytext=(mid_x, LAST_LEVEL - 6000),
    ha='center', va='center', color=DOWN, fontsize=11, fontweight='bold',
    linespacing=1.5, zorder=10,
)

# ---------------------------------------------------------------- axes formatting
ax.set_xlim(x[0] - 1.2, last_i + 7)
ax.set_ylim(y_bottom, y_top)
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:,.0f}K"))
ax.yaxis.tick_right()                       # 가격축 우측 (TradingView 스타일)
ax.tick_params(axis='y', colors=TEXT2, labelsize=12, length=0, pad=8)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

# x ticks: Mon YYYY, <=5
tick_idx = np.linspace(0, last_i, 5).round().astype(int)
ax.set_xticks(tick_idx)
ax.set_xticklabels([df['date'].iloc[i].strftime('%b %Y') for i in tick_idx])
ax.tick_params(axis='x', colors=TEXT2, labelsize=12, length=0, pad=8)

fig.subplots_adjust(left=0.015, right=0.935, top=0.97, bottom=0.10)

png, svg = save_chart(fig, 'btc_weekly_drawdown', output_dir='outputs/charts/bitcoin/price')
print('saved:', png)
print(f'drawdown {DD_ABS:,.2f} ({DD_PCT:.2f}%)')
