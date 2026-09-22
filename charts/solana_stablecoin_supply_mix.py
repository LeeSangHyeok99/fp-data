"""
Solana's settlement cash: stablecoin supply mix at end of Q2 2026 (horizontal bars).
소스: Blockworks Q2 PDF p.26 (레퍼런스 수치 USDC 47 / USDT 24 / Other 29).
투명 배경, 1600px 슬롯 폭 1:1. 제목/범례/출처는 assemble 단계.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart  # noqa: E402

setup_font()
df = pd.read_csv('outputs/data/solana_stablecoin_supply_mix_q2_2026.csv')

# 프레임은 콘텐츠 폭(1280)에 맞춘다. assemble에서 --chart-size 1280 430으로 1:1 배치.
W, H = 1280, 430
PX2PT = 0.72
SLATE, GOLD = ('#232B36', '#3C4653'), ('#4D3D1D', '#B8923A')   # (fill, border)
TEXT = '#D1D4DC'
X0, MAXW, BAR_H, PITCH, Y0 = 300, 860, 56, 160, 35
vmax = df['share_pct'].max()

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

for i, r in df.iterrows():
    y = Y0 + i * PITCH; w = MAXW * r['share_pct'] / vmax
    fill, border = GOLD if r['token'] == 'USDC' else SLATE
    rr, g, b = mcolors.to_rgb(fill); f = np.linspace(1.18, 0.82, 256)[:, None]
    grad = np.dstack([np.clip(rr * f, 0, 1), np.clip(g * f, 0, 1), np.clip(b * f, 0, 1), np.full_like(f, 0.95)])
    im = ax.imshow(grad, aspect='auto', extent=[X0, X0 + w, y + BAR_H, y], interpolation='bilinear', zorder=2)
    clip = FancyBboxPatch((X0, y), w, BAR_H, boxstyle='round,pad=0,rounding_size=4', transform=ax.transData,
                          facecolor='none', edgecolor=border, linewidth=1.4, zorder=3)
    ax.add_patch(clip); im.set_clip_path(clip)
    ax.text(0, y + BAR_H / 2, r['token'], ha='left', va='center', fontsize=29 * PX2PT, fontweight='bold', color=TEXT)
    ax.text(X0 + w + 24, y + BAR_H / 2, f"{r['share_pct']}%", ha='left', va='center', fontsize=30 * PX2PT, fontweight='bold', color=TEXT)
ax.set_xlim(0, W); ax.set_ylim(H, 0)

png, svg = save_chart(fig, 'solana_stablecoin_supply_mix', 'outputs/charts/solana/stablecoin', tight=False)
plt.close(fig); print(png)
