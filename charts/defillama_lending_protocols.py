"""
Leading Lending Protocols (DefiLlama)
가로 스택 바. TVL(유휴 유동성) + Active Loans(대출 잔액) = Supplied(총 예치).
소스: DefiLlama Lending 카테고리 스냅샷.
"""
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/defillama_lending_protocols.csv'

C_TVL   = '#5470c6'   # TVL (유휴 유동성)
C_LOANS = '#73c0de'   # Active Loans (대출 잔액)

LABEL_FONT = 17       # 프로토콜명
VALUE_FONT = 16       # 바 끝 합계 라벨
SEG_FONT   = 14       # 세그먼트 안 시리즈 라벨

X_MAX   = 34
X_TICKS = [0, 10, 20, 30]
BAR_H   = 0.62

OUT_NAME = 'defillama_lending_protocols'
OUT_DIR  = 'outputs/charts/defi/lending'
# ======================================================================

TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH).sort_values('tvl')  # barh는 아래부터 → 오름차순
y = np.arange(len(df))

fig, ax = plt.subplots(figsize=(10.67, 7.6), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.barh(y, df['tvl'], height=BAR_H, color=C_TVL, zorder=3)
ax.barh(y, df['active_loans'], left=df['tvl'], height=BAR_H, color=C_LOANS, zorder=3)

for yi, (t, l, s) in enumerate(zip(df['tvl'], df['active_loans'], df['supplied'])):
    ax.text(s + 0.35, yi, f"${s:.2f}B", ha='left', va='center',
            color=TEXT, fontsize=VALUE_FONT, fontweight='bold', zorder=4)

# 시리즈 라벨은 가장 넓은 바(Aave) 안에 직접 표기 (범례 대신)
top = len(df) - 1
t_top, l_top = df['tvl'].iloc[-1], df['active_loans'].iloc[-1]
ax.text(t_top / 2, top, 'TVL', ha='center', va='center',
        color='#141414', fontsize=SEG_FONT, fontweight='bold', zorder=5)
ax.text(t_top + l_top / 2, top, 'Active Loans', ha='center', va='center',
        color='#141414', fontsize=SEG_FONT, fontweight='bold', zorder=5)

ax.set_xlim(0, X_MAX)
ax.set_ylim(-0.7, len(df) - 0.3)
ax.set_xticks(X_TICKS)
ax.set_xticklabels([f"${v}B" for v in X_TICKS])
ax.set_yticks(y)
ax.set_yticklabels(df['protocol'])

ax.tick_params(axis='x', labelsize=VALUE_FONT + 2, colors=TEXT2, length=0, pad=10)
ax.tick_params(axis='y', labelsize=LABEL_FONT, colors=TEXT2, length=0, pad=10)

ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

fig.tight_layout()
png, svg = save_chart(fig, OUT_NAME, OUT_DIR)
print(png, svg)
