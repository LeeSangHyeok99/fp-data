"""pump.fun vs 챌린저 3종 일별 수수료 (Aug 15 ~ Sep 7, 2026).

레퍼런스 재현. 데이터는 DefiLlama dailyFees 실데이터.
pump.fun은 본딩커브(PumpSwap 별도 프로토콜), Pons는 V2(Robinhood Chain),
FOMO는 Solana + Hyperliquid L1(Robinhood Chain 제외).
FOMO 9/7은 Solana 어댑터 지연으로 부분집계라 공란 처리(레퍼런스도 9/6에서 끊긴다).
StonkFun만 레퍼런스 픽셀 추출값. DefiLlama가 며칠 지연 + 약 20% 과소집계라
레퍼런스는 플랫폼 자체 리포트를 썼는데, stonkfun.xyz 배포가 내려가 있어 재취득 불가
(DefiLlama 기준 9/6 $804K, 9/7 $243K vs 레퍼런스 $1.50M, $1.21M).
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, save_chart

SERIES = {                       # 레퍼런스 색 구성 그대로
    'pumpfun': '#FFFFFF',
    'pons_v2': '#4ED6B0',
    'fomo': '#9B8AF0',
    'stonkfun': '#2EC4CC',
}

df = pd.read_csv('outputs/data/pumpfun_vs_challengers_daily_fees.csv',
                 parse_dates=['date'])

# 레퍼런스 부제의 역전 주장 검증
d = df.set_index('date')
assert (d.loc['2026-08-29':, 'pons_v2'] > d.loc['2026-08-29':, 'pumpfun']).all()
assert (d.loc['2026-09-03':'2026-09-04', 'fomo'] > d.loc['2026-09-03':'2026-09-04', 'pumpfun']).all()
assert d.loc['2026-09-06', 'stonkfun'] > d.loc['2026-09-06', 'pumpfun']

fig, ax = create_figure('line')

for col, color in SERIES.items():
    ax.plot(df['date'], df[col] / 1e6, color=color, linewidth=2.0,
            solid_joinstyle='round', solid_capstyle='round', zorder=4)

ax.set_ylim(0, 11.6)
ax.set_yticks([0, 5, 10])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(df['date'].min(), df['date'].max())
ax.set_xticks(df['date'][::4])  # 시작일(8/15) 기준 4일 간격
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)  # 45도 회전은 apply_style 기본값

print(save_chart(fig, 'pumpfun_vs_challengers_daily_fees',
                 'outputs/charts/pumpfun/fees')[0])
