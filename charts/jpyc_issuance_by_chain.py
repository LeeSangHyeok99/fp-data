"""
JPYC Issuance Volume by Chain + Market Cap line (dual axis)
소스: Dune jpyc_mint&redeem (dune.com/queries/6064376), 실데이터 CSV.
좌축: 누적 발행량(net supply) by chain, stacked area (JPY)
우축: 시가총액(= 총 net supply) line (USD)
four-pillars dark theme.

──────────────────────────────────────────────────────────────────────
편집 방법: 아래 "✏️ EDIT HERE" 블록의 값만 바꾸면 차트가 바뀝니다.
          (그 아래 RENDER 영역은 건드리지 않아도 됩니다.)
──────────────────────────────────────────────────────────────────────
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 / 기간 --------------------------------------------------
CSV_PATH   = 'outputs/data/jpyc_net_supply_by_chain.csv'
START_DATE = '2025-10-20'   # 차트 시작일 (왼쪽 빈 구간 잘라내기. 발행 시작 ~10/27)
FX         = 160.2          # JPY/USD 환율 (2026-06-16, Frankfurter/ECB 교차확인)

# --- 2. 체인 색상 (스택 아래→위 순서) ----------------------------------
CH = [
    ('polygon',   '#8247e5'),   # Polygon 퍼플
    ('avalanche', '#e84142'),   # Avalanche 레드
    ('ethereum',  '#627eea'),   # Ethereum 블루
    ('kaia',      '#bff009'),   # Kaia 라임그린
]

# --- 3. 폰트 크기 ------------------------------------------------------
TICK_FONT   = 24       # x·y축 라벨 폰트

# --- 4. x축 라벨 회전 (대각선) + 틱마크 --------------------------------
X_ROTATION  = 45       # 0이면 수평, 45면 대각선
X_LABEL_HA  = 'right'
X_INTERVAL  = 2        # 월 라벨 간격 (2 = 2개월마다)
TICK_LENGTH = 6        # 틱마크 길이 (0이면 숨김)
TICK_WIDTH  = 1.2      # 틱마크 두께

# --- 5. 축 범위 / 눈금 -------------------------------------------------
LEFT_TOP    = 1000                    # 좌축 최대 (¥M)
LEFT_TICKS  = [0, 250, 500, 750, 1000]

# 출력 파일명 / 경로
OUT_NAME = 'jpyc_issuance_by_chain'
OUT_DIR  = 'outputs/charts/jpyc/issuance'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

BG = COLORS['background']
TEXT2 = COLORS['text_secondary']

df = pd.read_csv(CSV_PATH, parse_dates=['date'])
df = df[df['date'] >= START_DATE].reset_index(drop=True)
x = df['date']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2 = ax.twinx()
for a in (ax, ax2):
    a.set_facecolor('none')
    for s in a.spines.values():
        s.set_visible(False)

# 좌축: net supply 스택 영역
ax.stackplot(x, *[df[name] for name, _ in CH],
             colors=[c for _, c in CH], edgecolor='none', alpha=0.92, zorder=3)

# 우축: 시가총액 라인 (총 net supply → USD 환산). 좌축과 동일 곡선이라 영역 상단에 맞물림
ax2.plot(x, df['total'] / FX, color='#f2f2f2', linewidth=1.8, alpha=0.92, zorder=5)

# x축
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=X_INTERVAL))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(x.iloc[0], x.iloc[-1] + pd.Timedelta(days=4))
ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT,
               length=TICK_LENGTH, width=TICK_WIDTH, pad=8)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=X_ROTATION,
         ha=(X_LABEL_HA if X_ROTATION else 'center'),
         rotation_mode='anchor')

# 좌축 y: 발행량 ¥M
ax.set_ylim(0, LEFT_TOP)
ax.set_yticks(LEFT_TICKS)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"¥{v:,.0f}M"))
ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT, length=0)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

# 우축 y: 시가총액 $M, 좌축 그리드라인과 동일 위치로 정렬
ax2.set_ylim(0, LEFT_TOP / FX)
ax2.set_yticks([t / FX for t in LEFT_TICKS])
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.1f}M"))
ax2.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT, length=0)
ax2.grid(False)

fig.subplots_adjust(left=0.11, right=0.90, top=0.97, bottom=0.20)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
last = df.iloc[-1]
print(f"total {last['total']:.0f}M JPY = ${last['total']/FX:.2f}M")
