"""
Japan crypto trading notional by fiscal year (FY16–FY24) — stacked bar
Spot trading (blue) + Margin/derivatives (orange), trillion yen notional.
Regulatory-event callouts mark the fiscal year each rule took effect.

Source: JVCEA primary statistics. Two sources, stitched and cross-checked.
        FY16–19: JVCEA 2019年度 annual report (tokei_20201120.pdf, saved under
                 sources/JVCEA_2019nendo_tokei_20201120.pdf), "取引金額推移"
                 table (単位:億円): 2016年度 現物15,369 / 証拠金19,790;
                 2017年度 127,140 / 564,325; 2018年度 94,138.36 / 765,300.60;
                 2019年度 76,552.34 / 692,100.49. (億円 → 兆円: ÷10,000.)
        FY19–24: JVCEA monthly statistics (会員の暗号資産取引状況表, 2026-06-04
                 release), 現物/証拠金 金額 (百万円) summed over Apr–Mar.
        Cross-check: FY19 matches between both sources — annual report
                     7.66 / 69.21 vs monthly-sum 7.66 / 69.2 — so the FY16–18
                     annual figures join the FY19–24 monthly series cleanly.
        Spot = 現物取引; Margin/derivatives = 証拠金取引 (想定元本 / notional basis).
        Unit: trillion yen.
Style: four-pillars, transparent BG.

──────────────────────────────────────────────────────────────────────
편집 방법: 아래 "✏️ EDIT HERE" 블록의 값만 바꾸면 차트가 바뀝니다.
          (그 아래 RENDER 영역은 건드리지 않아도 됩니다.)
──────────────────────────────────────────────────────────────────────
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, FuncFormatter
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG

setup_font()

# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 (단위: 조엔 / trillion yen) -----------------------------
#     (회계연도, 현물 spot, 증거금·파생 margin)
DATA = [
    ('FY16',  1.54,  1.98),
    ('FY17', 12.71, 56.43),
    ('FY18',  9.41, 76.53),
    ('FY19',  7.66, 69.21),
    ('FY20', 20.60, 97.40),
    ('FY21', 28.50, 37.20),
    ('FY22', 10.00, 14.90),
    ('FY23', 11.30,  5.60),
    ('FY24', 20.60, 15.80),
]

# --- 2. 색상 -----------------------------------------------------------
SPOT_COLOR   = '#2f6fd0'   # 현물 (파랑, 막대 아래쪽)
MARGIN_COLOR = '#f0992e'   # 증거금/파생 (주황, 막대 위쪽)

# --- 3. 텍스트 / 라벨 (빈 문자열이면 숨김) ------------------------------
TITLE        = ''          # 예: 'Japan Trading Volume'  (보통 FP 템플릿에서 추가 → 비움)
Y_LABEL      = ''          # 예: 'Trillion yen (notional)'
FOOTNOTE     = '*FY16–18: JVCEA annual report; FY19–24: monthly statistics'

SHOW_LEGEND   = False       # True면 좌상단에 범례 표시
LEGEND_LABELS = ('Spot trading', 'Margin / derivatives')

# --- 4. 축 / 막대 ------------------------------------------------------
Y_MAX        = 155          # y축 최대값
Y_TICK_STEP  = 40           # y축 눈금 간격 (0, 40, 80, 120 …)
BAR_WIDTH    = 0.62

# --- 5. 규제 이벤트 콜아웃 ---------------------------------------------
#     각 콜아웃의 글자/색/위치를 자유롭게 수정하세요.
#       bar   : 어느 막대 위에 붙일지 (막대 index, 0부터)
#       text  : 표시할 글자 (\n 으로 줄바꿈)
#       color : 글자색 + 점 색
#       dx    : 좌우 미세 이동 (막대 폭 기준, +오른쪽 / -왼쪽). 기본 0
#       dy    : 글자 높이 미세 조정 (조엔 단위, +위 / -아래). 기본 0
#       size  : 글자 크기. 비우면 기본값 사용
#       ha    : 정렬 'center' / 'left' / 'right'. 기본 center
EVENT_DOT_GAP  = 3          # 막대 꼭대기에서 점까지 간격
EVENT_TEXT_GAP = 7          # 막대 꼭대기에서 글자까지 기본 간격
EVENT_SIZE     = 10.5       # 콜아웃 글자 기본 크기
EVENTS = []   # 막대 위 콜아웃 글자/점 모두 숨김

# 출력 파일명 / 경로
OUT_NAME = 'japan_crypto_trading_volume_fy'
OUT_DIR  = 'outputs/charts/macro/volume'
CSV_PATH = 'outputs/data/japan_crypto_trading_volume_fy.csv'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

df = pd.DataFrame(DATA, columns=['fy', 'spot', 'margin'])
df['total'] = df['spot'] + df['margin']
df.to_csv(CSV_PATH, index=False)

x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(12, 6.4), dpi=150)

ax.bar(x, df['spot'],  width=BAR_WIDTH, color=SPOT_COLOR,   zorder=3)
ax.bar(x, df['margin'], width=BAR_WIDTH, bottom=df['spot'],
       color=MARGIN_COLOR, zorder=3)

# Regulatory-event callouts
for ev in EVENTS:
    xi    = ev['bar']
    text  = ev['text']
    color = ev['color']
    dx    = ev.get('dx', 0)
    dy    = ev.get('dy', 0)
    size  = ev.get('size', EVENT_SIZE)
    ha    = ev.get('ha', 'center')
    top = df['total'].iloc[xi]
    ax.scatter(xi + dx, top + EVENT_DOT_GAP, s=22, color=color, zorder=5,
               edgecolors='none')
    ax.annotate(text, xy=(xi + dx, top + EVENT_TEXT_GAP + dy), ha=ha,
                va='bottom', fontsize=size, fontweight='bold', color=color,
                linespacing=1.25)

# Axes
ax.set_ylim(0, Y_MAX)
ax.yaxis.set_major_locator(MultipleLocator(Y_TICK_STEP))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'¥{v:.0f}T'))
ax.set_xticks(x)
ax.set_xticklabels(df['fy'])
ax.set_xlim(-0.6, len(df) - 0.4)

if TITLE:
    ax.set_title(TITLE, fontsize=20, fontweight='bold', color='#d1d4dc',
                 pad=16, loc='left')
if Y_LABEL:
    ax.set_ylabel(Y_LABEL, fontsize=AXIS_CONFIG['y_label']['fontsize'],
                  fontweight='bold', color=AXIS_CONFIG['y_label']['color'],
                  labelpad=AXIS_CONFIG['y_label']['labelpad'])

if SHOW_LEGEND:
    handles = [Patch(facecolor=SPOT_COLOR,   label=LEGEND_LABELS[0]),
               Patch(facecolor=MARGIN_COLOR, label=LEGEND_LABELS[1])]
    ax.legend(handles=handles, loc='upper left', frameon=False, fontsize=11,
              labelcolor='#d1d4dc')

# four-pillars styling
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', labelsize=24,
               pad=AXIS_CONFIG['y_tick']['pad'], length=0,
               colors=AXIS_CONFIG['y_tick']['color'])
ax.tick_params(axis='x', labelsize=24, pad=8, rotation=0,
               colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

if FOOTNOTE:
    ax.text(0.005, 0.985, FOOTNOTE, transform=ax.transAxes, fontsize=8.5,
            color='#9aa3ad', ha='left', va='top')

fig.tight_layout()

png, svg = save_chart(fig, OUT_NAME, OUT_DIR)
plt.close(fig)
print('saved:', png)
print(df.to_string(index=False))
