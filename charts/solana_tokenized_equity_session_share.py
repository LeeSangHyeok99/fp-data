"""
When tokenized equities trade: Solana onchain spot volume share by session
(single 100% horizontal bar) - four-pillars 내재화.
소스: Allium p.43 (레퍼런스 이미지 수치). 19 Aug 2025~18 Aug 2026 12개월.
투명 배경, 1600x360px 슬롯용 (제목/범례/출처는 assemble 단계).
"""
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, FancyBboxPatch

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart  # noqa: E402

setup_font()

df = pd.read_csv('outputs/data/solana_tokenized_equity_volume_by_session.csv')
assert df['share_pct'].sum() == 100

# 세그먼트 색 (fill, border). 첫 번째 = US regular(슬레이트), 나머지 = Outside(골드)
SLATE = ('#232B36', '#3C4653')
GOLD = ('#4D3D1D', '#B8923A')
STYLE = [SLATE, GOLD, GOLD]

W, H = 1600, 360               # px 좌표계 (인포그래픽 슬롯 폭과 1:1)
PX2PT = 72 / 100               # figure dpi 100 기준 px→pt
BAR_Y0, BAR_H = 40, 125
LABEL_Y = BAR_Y0 + BAR_H + 62
GAP = 4

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis('off')

x = 1.0
for (_, row), (fill, border) in zip(df.iterrows(), STYLE):
    w = (W - 2) * row['share_pct'] / 100 - (GAP if x + 1 < W - 1 else 0)
    # 세로 그라데이션: 위 밝게 → 아래 어둡게
    r, g, b = mcolors.to_rgb(fill)
    f = np.linspace(1.18, 0.82, 256)[:, None]
    grad = np.dstack([np.clip(r * f, 0, 1), np.clip(g * f, 0, 1),
                      np.clip(b * f, 0, 1), np.full_like(f, 0.95)])
    im = ax.imshow(grad, aspect='auto', extent=[x, x + w, BAR_Y0 + BAR_H, BAR_Y0],
                   interpolation='bilinear', zorder=2)
    clip = FancyBboxPatch((x, BAR_Y0), w, BAR_H, boxstyle='round,pad=0,rounding_size=4',
                          transform=ax.transData, facecolor='none', edgecolor=border,
                          linewidth=1.4, zorder=3)
    ax.add_patch(clip)
    im.set_clip_path(clip)
    ax.text(x + 22, BAR_Y0 + BAR_H / 2, f"{row['share_pct']:.0f}%", ha='left', va='center',
            fontsize=40 * PX2PT, fontweight='bold', color='#D1D4DC', zorder=5)
    ax.text(x, LABEL_Y, row['session'], ha='left', va='center',
            fontsize=26 * PX2PT, fontweight='bold', color='#9CA3AF', zorder=5)
    x += w + GAP

png, svg = save_chart(fig, 'solana_tokenized_equity_session_share',
                      'outputs/charts/tokenized_equities/volume', tight=False)
plt.close(fig)
print(png, svg)
