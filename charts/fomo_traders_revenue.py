"""FOMO: Solana 일별 활성 트레이더 + 월별 순매출 (인포그래픽 2장 세트).

두 차트는 같은 figsize/폰트로 그려 한 인포그래픽에 나란히 붙였을 때 비율이 맞는다.
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import DPI, apply_style, create_figure, gradient_rounded_bar, save_chart

MINT = '#A2E3CF'          # 레퍼런스(Blockworks) 시리즈 색
FIGSIZE = (9.0, 5.25)     # 1350 x 788 @150dpi, 두 차트 공통
FS_Y, FS_X = 16, 14
GEOM = [0.13, 0.20, 0.855, 0.77]  # 두 차트 공통 플롯 영역
OUT = 'outputs/charts/fomo/metrics'


def styled_axes():
    fig, ax = create_figure('line')
    fig.set_size_inches(*FIGSIZE)
    return fig, ax


def finish(fig, ax, name, kind='line'):
    apply_style(fig, ax, kind)  # tight_layout 포함 -> 위치 지정은 그 뒤에
    ax.tick_params(axis='y', labelsize=FS_Y)
    ax.tick_params(axis='x', labelsize=FS_X)
    ax.set_position(GEOM)       # 두 차트의 플롯 영역을 픽셀 단위로 일치시킨다
    print(save_chart(fig, name, OUT, tight=False)[0])


# =============================================================================
# 1. Daily active traders (Solana) - 레퍼런스 이미지에서 픽셀 추출
# =============================================================================
# 레퍼런스(Blockworks) 차트 픽셀 역산값. scripts/extract_fomo_traders_from_reference.py
# Dune(@adam_tehc query 7856688)에도 Solana wallets_dedup 실데이터가 있지만
# 2026-03부터만 있고 7월 Robinhood Chain 확장 이후 정의가 갈려 9월엔 1.7배가 된다.
# 이 차트는 레퍼런스 재현이 목적이라 원본 계열을 쓴다.
tr = pd.read_csv('outputs/data/fomo_daily_active_traders_solana.csv',
                 parse_dates=['date'])

fig, ax = styled_axes()
ax.plot(tr['date'], tr['active_traders'], color=MINT, linewidth=1.8,
        solid_joinstyle='round', zorder=4)

ax.set_ylim(0, 95_000)
ax.set_yticks([0, 20_000, 40_000, 60_000, 80_000])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))
# 마지막 급반등 선이 오른쪽 축에 붙어 잘려 보여서 3일치 여백을 준다
ax.set_xlim(tr['date'].min(), tr['date'].max() + pd.Timedelta(days=3))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[7, 10, 1, 4]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

finish(fig, ax, 'fomo_daily_active_traders_solana')

# =============================================================================
# 2. Monthly net revenue - Blockworks Research 일별 순매출을 월 합산
# =============================================================================
rev = pd.read_csv('outputs/data/fomo_net_revenue.csv',
                  parse_dates=['date']).set_index('date')['net_revenue_usd']

# 스냅샷을 8/30에 떠서 마지막 3일이 미확정 부분집계(정산일 대비 비율 0.73/0.40/0.76)
# 이고 8/31은 아예 없다. 그대로 합치면 8월 바가 $12.7M로 1.3M 과소집계된다.
# DefiLlama 일별 revenue x 8/21~8/27 정산일 비율 중앙값(0.9054)으로 4일치를 대체.
# 블록웍스 구독 데이터를 다시 뽑으면 이 블록은 지운다.
patch = pd.Series({pd.Timestamp(d): v for d, v in {
    '2026-08-28': 606_214, '2026-08-29': 612_370,
    '2026-08-30': 841_992, '2026-08-31': 743_448}.items()})
rev = patch.combine_first(rev)  # 8/31은 원본에 없으므로 update가 아니라 combine

m = rev.sort_index().resample('MS').sum().loc['2025-07-01':'2026-08-01']
assert abs(m.loc['2026-08-01'] - 14.0e6) < 0.2e6, m.loc['2026-08-01']

fig, ax = styled_axes()
ax.set_ylim(0, 15_000_000)
ax.set_xlim(-0.7, len(m) - 0.3)
ax.set_yticks([0, 5_000_000, 10_000_000, 15_000_000])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v/1e6:.0f}M'))
ax.set_xticks(range(len(m)))
ax.set_xticklabels([d.strftime('%b %Y') for d in m.index])

for i, v in enumerate(m.values):
    gradient_rounded_bar(ax, i, 0.62, v, MINT, floor=0.55, round_top=False)

finish(fig, ax, 'fomo_monthly_net_revenue', 'bar')
