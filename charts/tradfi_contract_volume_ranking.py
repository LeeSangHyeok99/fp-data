"""
Expanded TradFi Contract Volume Ranking
소스: RootData (2026 Surge: Stock Derivatives), 24h volume USD millions, CoinClass snapshot Sep 11, 2026.
Notion agent HTML(05b_expanded_tradfi_volume_notion_agent_chart.html) 재현.
가로 바 13개, 1위 SanDisk만 강조색, 나머지 블루. 레퍼런스 색 구성 그대로.
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, SERIES_COLORS, gradient_barh, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/tradfi_contract_volume_ranking.csv'

HIGHLIGHT = SERIES_COLORS[6]   # 오렌지 (1위)
BASE      = SERIES_COLORS[0]   # 블루 (나머지)

TICK_FONT  = 18
VALUE_FONT = 16
BAR_HEIGHT = 0.62
GRAD_FLOOR = 0.80
X_MAX      = 1000
X_TICKS    = [0, 200, 400, 600, 800, 1000]
VALUE_GAP  = 12

OUT_NAME = 'tradfi_contract_volume_ranking'
OUT_DIR  = 'outputs/charts/tokenized-equities/volume'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
y = np.arange(len(df))

fig, ax = plt.subplots(figsize=(17.0, 7.0), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

for yi, v in zip(y, df['volume_musd']):
    c = HIGHLIGHT if yi == 0 else BASE
    rect = ax.barh(yi, v, height=BAR_HEIGHT, color=c, zorder=3)[0]
    gradient_barh(ax, rect, c, floor=GRAD_FLOOR)
    ax.text(v + VALUE_GAP, yi, f"${v:,.0f}M", ha='left', va='center',
            color=TEXT, fontsize=VALUE_FONT, fontweight='bold', zorder=4)

# imshow가 축 범위를 건드리므로 되돌린다
ax.set_xlim(0, X_MAX)
ax.set_ylim(len(df) - 0.5, -0.5)

ax.set_yticks(y)
ax.set_yticklabels(df['contract'])
ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT, length=0, pad=12)

ax.set_xticks(X_TICKS)
ax.set_xticklabels([f"${t:,.0f}M" for t in X_TICKS])
ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT, length=6, width=1.2, pad=8)
ax.grid(True, axis='x', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.tight_layout()
png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
print(f"total ${df['volume_musd'].sum():,.1f}M")
