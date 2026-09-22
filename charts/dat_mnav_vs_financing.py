"""
Basic mNAV vs. Last Financing Date (Digital Asset Treasuries) — scatter
각 점 = DAT 티커. x축 마지막 펀딩일, y축 Basic mNAV(시총/순자산가치 배수).
레퍼런스 산점도 내재화. 색(blue/red)은 레퍼런스 그대로.
값/날짜는 제공된 표로 교차 확인(9개 정확), 나머지는 산점도에서 추출.
오프스케일(별표) ZONE 3.56, GMEX 2.16은 원본과 동일하게 제외.
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

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 (CSV에서 로드) ------------------------------------------
CSV_PATH = 'outputs/data/dat_mnav_vs_financing.csv'   # ticker, asset, mnav, date, color

# --- 2. 색상 (레퍼런스 그대로) -----------------------------------------
COLOR_MAP = {
    'blue': '#2f6fd0',
    'red':  '#e0473e',
}

# --- 3. 폰트 / 점 크기 -------------------------------------------------
X_TICK_FONT = 28       # x축 라벨 폰트
Y_TICK_FONT = 27       # y축 라벨 폰트
LABEL_FONT = 13        # 점 옆 티커 라벨 폰트
DOT_SIZE   = 76        # 점 크기

# --- 4. x축 ----------------------------------------------------------
X_ROTATION = 45
X_MIN = '2025-07-08'   # x축 시작
X_MAX = '2026-06-28'   # x축 끝

# --- 5. y축 (Basic mNAV) ----------------------------------------------
Y_TICKS = [0.0, 0.5, 1.0, 1.5]
Y_MIN   = 0.05
Y_MAX   = 1.5

# --- 6. 티커 라벨 위치 미세조정 (기본은 점 오른쪽 위) ------------------
#   기본 offset = (오른쪽 6pt, 위 6pt). 겹치는 점만 여기서 조정.
#   {티커: (dx_pt, dy_pt, ha)}  ha = 'left'/'right'
LABEL_DEFAULT = (6, 6, 'left')
LABEL_OVERRIDES = {
    'MSTR': (-8, 10, 'right'),
    'HSDT': (9, -13, 'left'),
    'DFDV': (6, -16, 'left'),
    'AVAT': (8, 2, 'left'),
}

# 출력 파일명 / 경로
OUT_NAME = 'dat_mnav_vs_financing'
OUT_DIR  = 'outputs/charts/dat/mnav'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']

df = pd.read_csv(CSV_PATH, parse_dates=['date'])
df['c'] = df['color'].map(COLOR_MAP)

fig, ax = plt.subplots(figsize=(14.5, 5.6), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.scatter(df['date'], df['mnav'], s=DOT_SIZE, c=df['c'],
           edgecolors='none', zorder=4)

for _, r in df.iterrows():
    dx, dy, ha = LABEL_OVERRIDES.get(r['ticker'], LABEL_DEFAULT)
    ax.annotate(r['ticker'], xy=(r['date'], r['mnav']),
                xytext=(dx, dy), textcoords='offset points',
                ha=ha, va='center', fontsize=LABEL_FONT,
                fontweight='bold', color=TEXT, zorder=5)

# x축 (Mon YYYY)
ax.set_xlim(pd.Timestamp(X_MIN), pd.Timestamp(X_MAX))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x', colors=TEXT2, labelsize=X_TICK_FONT,
               length=6, width=1.1, pad=8)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=X_ROTATION,
         ha='right', rotation_mode='anchor')

# y축 (Basic mNAV)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_yticks(Y_TICKS)
ax.tick_params(axis='y', colors=TEXT2, labelsize=Y_TICK_FONT, length=0)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.06, right=0.985, top=0.97, bottom=0.13)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
print(df[['ticker', 'mnav', 'date']].to_string(index=False))
