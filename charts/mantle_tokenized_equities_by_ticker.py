"""
Tokenized Equities Minted on Mantle by Ticker (2026-09-10)
레퍼런스 이미지 재현. 수평 바, 2026 IPO 코호트(민트) / April 2026 US 코호트(블루).
값은 레퍼런스 라벨(xStock totalSupply x CoinGecko 가격) 그대로.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, GRID_CONFIG, gradient_barh, save_chart  # noqa: E402

setup_font()

CSV_PATH = 'outputs/data/mantle_tokenized_equities_by_ticker.csv'
PALETTE = {'april_2026': '#5B6BE8', 'ipo_2026': '#6EE7C8'}
TICKER_FONT = 20
VALUE_FONT = 19
SUB_FONT = 16
TICK_FONT = 20
BAR_HEIGHT = 0.62
GRAD_FLOOR = 0.82
X_MAX = 12.0
X_TICKS = [0, 3, 6, 9, 12]
VALUE_GAP_PX = 12
OUT_NAME = 'mantle_tokenized_equities_by_ticker'
OUT_DIR = 'outputs/charts/mantle/rwa'

TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
df['value_m'] = df['value_usd'] / 1e6
ys = list(range(len(df)))

fig, ax = plt.subplots(figsize=(14, 6.2), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for sp in ax.spines.values():
    sp.set_visible(False)

Y_LO, Y_HI = len(df) - 0.5, -0.5
ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for y, row in zip(ys, df.itertuples()):
    color = PALETTE[row.cohort]
    rect = ax.barh(y, row.value_m, height=BAR_HEIGHT, color=color, zorder=3)[0]
    gradient_barh(ax, rect, color, floor=GRAD_FLOOR)
ax.set_xlim(0, X_MAX)   # imshow가 축을 건드리므로 되돌린다
ax.set_ylim(Y_LO, Y_HI)

ax.set_yticks(ys)
ax.set_yticklabels(df['ticker'])
ax.tick_params(axis='y', labelsize=TICKER_FONT, colors=TEXT, length=0, pad=8)
ax.set_xticks(X_TICKS)
ax.set_xticklabels([f'${t:.0f}M' for t in X_TICKS])
ax.tick_params(axis='x', labelsize=TICK_FONT, colors=TEXT2, length=6, pad=8)

val_texts = []
for y, row in zip(ys, df.itertuples()):
    v = f'${row.value_m:.0f}M' if row.value_m >= 10 else f'${row.value_m:.1f}M'
    t = ax.text(row.value_m + 0.15, y, v, ha='left', va='center', color=TEXT,
                fontsize=VALUE_FONT, fontweight='bold', zorder=4)
    val_texts.append((t, y, f'{row.shares:,.0f} Sh'))

fig.tight_layout()
fig.canvas.draw()
inv = ax.transData.inverted()
for t, y, sub in val_texts:
    bb = t.get_window_extent(fig.canvas.get_renderer())
    x_sub = inv.transform((bb.x1 + VALUE_GAP_PX, bb.y0))[0]
    ax.text(x_sub, y, sub, ha='left', va='center', color=TEXT2,
            fontsize=SUB_FONT, fontweight='bold', zorder=4)

print(save_chart(fig, OUT_NAME, OUT_DIR))
