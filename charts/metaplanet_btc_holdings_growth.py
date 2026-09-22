"""
Metaplanet Inc. Bitcoin Holdings Growth (BTC held)
레퍼런스(Mermaid xychart) 내재화: Metaplanet Inc. Bitcoin Holdings
1:1 정사각 비율, four-pillars dark theme.

──────────────────────────────────────────────────────────────────────
편집 방법: 아래 "✏️ EDIT HERE" 블록의 값만 바꾸면 차트가 바뀝니다.
          (그 아래 RENDER 영역은 건드리지 않아도 됩니다.)
──────────────────────────────────────────────────────────────────────
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart, area_glow, endpoint_dot  # noqa: E402

setup_font()
# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 (CSV에서 로드) ------------------------------------------
CSV_PATH = 'outputs/data/metaplanet_btc_holdings_growth.csv'   # quarter, btc_held

# --- 2. 색상 -----------------------------------------------------------
BTC_ORANGE  = '#f7931a'

# --- 3. 폰트 크기 ------------------------------------------------------
TICK_FONT   = 20       # x·y축 라벨 폰트
VALUE_FONT  = 16       # 끝점 값 라벨 폰트

# --- 4. x축 라벨 회전 (대각선) -----------------------------------------
X_ROTATION  = 45       # 0이면 수평, 45면 대각선
X_LABEL_HA  = 'right'

# --- 5. 틱마크 --------------------------------------------------------
TICK_LENGTH = 6        # 틱마크 길이 (0이면 숨김)
TICK_WIDTH  = 1.2      # 틱마크 두께

# --- 6. 축 / 라인 ------------------------------------------------------
Y_MAX       = 40000
Y_TICKS     = [0, 10000, 20000, 30000, 40000]
LINE_WIDTH  = 2.4
VALUE_GAP   = 1700     # 끝점에서 값 라벨까지 간격

# 출력 파일명 / 경로
OUT_NAME = 'metaplanet_btc_holdings_growth'
OUT_DIR  = 'outputs/charts/bitcoin/treasury'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
x = np.arange(len(df))
y = df['btc_held'].values

fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

area_glow(ax, x, y, color=BTC_ORANGE)
ax.plot(x, y, color=BTC_ORANGE, linewidth=LINE_WIDTH, zorder=4)
endpoint_dot(ax, x[-1], y[-1], color=BTC_ORANGE, size=70)
ax.text(x[-1], y[-1] + VALUE_GAP, f"{y[-1]:,.0f}", ha='right', va='bottom',
        color=TEXT, fontsize=VALUE_FONT, fontweight='bold')

# 축
ax.set_xlim(-0.15, len(df) - 0.6)
ax.set_ylim(0, Y_MAX)
ax.set_xticks(x)
ax.set_xticklabels(df['quarter'], rotation=X_ROTATION,
                   ha=(X_LABEL_HA if X_ROTATION else 'center'))
ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT,
               length=TICK_LENGTH, width=TICK_WIDTH, pad=8)

ax.set_yticks(Y_TICKS)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:,.0f}K"))
ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT,
               length=TICK_LENGTH, width=TICK_WIDTH, pad=8)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.16)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
