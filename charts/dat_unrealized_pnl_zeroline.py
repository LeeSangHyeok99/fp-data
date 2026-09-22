"""
Unrealized P&L of Digital Asset Treasuries (DATs)
레퍼런스(Artemis "Unrealized P&L DATs", classic.artemis.ai/digital-asset-treasuries) 내재화.
DAT 토큰 포지션의 평균 매입단가 대비 미실현 손익(USD). 대부분 적자, Hyperliquid Strategies만 흑자.
값은 Artemis 대시보드(1Y) 스크린샷에서 추출 (2026-06 갱신). 방향/스케일은 The Block·NewsBTC 기사로 교차 확인.
상위 2개(Bitmine/Strategy)는 −$9B대, 중위는 −$1B대로 대시보드와 정합.
four-pillars dark theme.

──────────────────────────────────────────────────────────────────────
편집 방법: 아래 "✏️ EDIT HERE" 블록의 값만 바꾸면 차트가 바뀝니다.
          (그 아래 RENDER 영역은 건드리지 않아도 됩니다.)
──────────────────────────────────────────────────────────────────────
"""
import sys
import textwrap
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 (CSV에서 로드) ------------------------------------------
CSV_PATH = 'outputs/data/dat_unrealized_pnl.csv'   # company, unrealized_pnl_usd_b, color

# --- 2. 폰트 크기 ------------------------------------------------------
TICK_FONT  = 24        # y축 라벨 폰트
XLABEL_FONT = 20       # x축 회사명 폰트

# --- 3. x축 라벨 ------------------------------------------------------
WRAP_WIDTH = 100       # 회사명 줄바꿈 폭 (글자수) — 크게 두면 한 줄
X_ROTATION = 45        # 0이면 수평, 45면 대각선

# --- 4. 축 범위 / 눈금 (단위: $B) -------------------------------------
Y_TICKS = [2.5, 0, -2.5, -5, -7.5, -10]   # 대시보드와 동일한 6개 눈금
Y_MIN   = -10.6
Y_MAX   = 2.8

# --- 5. 막대 ----------------------------------------------------------
BAR_WIDTH = 0.72

# 출력 파일명 / 경로
OUT_NAME = 'dat_unrealized_pnl_zeroline'
OUT_DIR  = 'outputs/charts/dat/treasury'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

TEXT2 = COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
x = np.arange(len(df))
vals = df['unrealized_pnl_usd_b'].values
colors = df['color'].tolist()
labels = ['\n'.join(textwrap.wrap(c, WRAP_WIDTH)) for c in df['company']]

fig, ax = plt.subplots(figsize=(14.5, 5.8), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.bar(x, vals, width=BAR_WIDTH, color=colors, zorder=3)

# 축
ax.set_xlim(-0.7, len(df) - 0.3)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=X_ROTATION,
                   ha=('right' if X_ROTATION else 'center'),
                   rotation_mode='anchor')
ax.tick_params(axis='x', colors=TEXT2, labelsize=XLABEL_FONT, length=5, width=1.0, pad=6)

ax.set_yticks(Y_TICKS)
def _fmt(v, _):
    if v < 0:
        return f"(${abs(v):,.1f}B)".replace('.0B', 'B')
    return f"${v:,.1f}B".replace('.0B', 'B')
ax.yaxis.set_major_formatter(FuncFormatter(_fmt))
ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT, length=5, width=1.0)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

# 0 기준선 강조 (진하게)
ax.axhline(0, color=COLORS['text'], alpha=0.95, linewidth=2.2, zorder=5)

fig.subplots_adjust(left=0.07, right=0.99, top=0.97, bottom=0.34)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
print(df[['company', 'unrealized_pnl_usd_b']].to_string(index=False))
