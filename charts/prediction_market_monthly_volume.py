import sys

import matplotlib

matplotlib.use('Agg')
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, gradient_bars, pixel_grid_figure, save_chart

# =============================================================================
# Data: The Block, Polymarket / Polymarket US / Kalshi monthly volume
# =============================================================================
df = pd.read_csv('outputs/data/prediction_market_monthly_volume.csv',
                 parse_dates=['month'])
# 2024년 전은 월 $10M 미만이라 축에서 보이지 않는 구간이라 자른다
df = df[df['month'] >= '2024-01-01'].reset_index(drop=True)

# 레퍼런스(The Block) 시리즈 색 그대로
SERIES = [('kalshi_usd', '#1F3FD8'),        # Kalshi (블루)
          ('polymarket_usd', '#EE5555'),    # Polymarket (레드)
          ('polymarket_us_usd', '#2AB7CA')]  # Polymarket US (틸)
MONTH_PX, BAR_PX = 40, 30

fig, ax, geom = pixel_grid_figure(len(df), MONTH_PX, ax_h=470)

ax.set_yticks([0, 25e9, 50e9])
ax.set_yticklabels(['$0B', '$25B', '$50B'])
ax.set_ylim(0, 56e9)

# 월은 길이가 달라 날짜축을 쓰면 칸 폭이 어긋난다. 인덱스를 x로 쓴다
x = np.arange(len(df))
ax.set_xlim(-0.5, len(df) - 0.5)
ticks = x[::3]
ax.set_xticks(ticks)
ax.set_xticklabels([d.strftime('%b %Y') for d in df['month'].iloc[ticks]])

bottoms = np.zeros(len(df))
for col, color in SERIES:
    gradient_bars(ax, x, df[col].values, color, MONTH_PX, BAR_PX,
                  floor=0.5, bottoms=bottoms, per_bar=True)
    bottoms = bottoms + df[col].values

apply_style(fig, ax, 'bar')  # tight_layout 포함 → 위치 지정은 그 뒤에
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=12)
ax.set_position(geom)

print(save_chart(fig, 'prediction_market_monthly_volume',
                 'outputs/charts/prediction-markets/volume', tight=False)[0])
