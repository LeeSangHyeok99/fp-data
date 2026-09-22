"""
Market cap of public bitcoin miners, Aug 28 2026 (four-pillars horizontal bar).
Data: sources/data7_market_cap.csv (시총은 close_usd x shares_outstanding로 검산)
"""

import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

setup_font()

# 전환 완료 / 전환 중 / 채굴 중심
CAT_COLOR = {'전환 완료 / AI 인프라 중심': '#6b5a7d',
             '전환 중': '#636b73',
             '채굴 중심': '#2a8d80'}

df = pd.read_csv('sources/data7_market_cap.csv')
df['mcap'] = df['close_usd'] * df['shares_outstanding'] / 1e9
df = df.sort_values('mcap', ascending=False).reset_index(drop=True)
y = np.arange(len(df))

fig, ax = plt.subplots(figsize=(14.2, 6.4), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')


def grad_bar(ax, yi, h, v, color, floor=0.68):
    """0 쪽이 어둡고 막대 끝으로 갈수록 밝아지는 가로 그라데이션 막대."""
    r, g, b = mcolors.to_rgb(color)
    f = floor + (1 - floor) * np.linspace(0, 1, 256) ** 0.5
    grad = np.stack([r * f, g * f, b * f, np.ones(256)], axis=-1)[None, :, :]
    ax.imshow(grad, aspect='auto', origin='lower', interpolation='bilinear',
              extent=[0, v, yi - h / 2, yi + h / 2], zorder=3)


for yi, row in df.iterrows():
    grad_bar(ax, yi, 0.62, row['mcap'], CAT_COLOR[row['category']])
    ann = ax.annotate(f"${row['mcap']:.1f}B", xy=(row['mcap'], yi), xytext=(10, 0),
                      textcoords='offset points', ha='left', va='center',
                      fontsize=13, fontweight='bold', color=COLORS['text'],
                      zorder=5)
    if not pd.isna(row['q2_2026_btc_mined']):
        # 채굴량 주석은 값 라벨 뒤에 회색으로 이어 붙인다.
        ax.annotate(f"(Q2 Mining {int(row['q2_2026_btc_mined']):,} BTC)",
                    xycoords=ann, xy=(1, 0), xytext=(8, 0),
                    textcoords='offset points', ha='left', va='bottom',
                    fontsize=12, fontweight='bold',
                    color=COLORS['text_secondary'], zorder=5)

ax.set_xlim(0, 21)
ax.set_ylim(len(df) - 0.5, -0.5)   # imshow가 축을 이미지에 맞추므로 여백 복구
ax.set_xticks([0, 5, 10, 15, 20])
ax.set_xticklabels([f'${t}B' for t in (0, 5, 10, 15, 20)], fontweight='bold')
ax.set_yticks(y)
ax.set_yticklabels(df['company'], fontweight='bold')

ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', length=0, colors=COLORS['text_secondary'],
               labelsize=15, pad=10)
ax.tick_params(axis='y', length=0, colors=COLORS['text'], labelsize=14, pad=12)

fig.tight_layout()
print(save_chart(fig, 'miner_market_cap_ranking',
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
