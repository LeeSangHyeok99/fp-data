"""
Change in realized hashrate, Q4 2025 to Q2 2026 (four-pillars horizontal bar).
Data: sources/data6_realized_hashrate_change.csv (변화율은 EH/s 원값에서 재계산 확인)
"""

import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

setup_font()

TEAL, GRAY, NAVY, RED = '#2d8e86', '#6b6e75', '#1d2639', '#af372c'

items = [
    ('Bitdeer', 44.2, TEAL),
    ('Entire Network (Quarterly Avg)', -10.6, GRAY),
    ('Public Miners Total', -13.4, NAVY),
    ('Public Miners ex Bitdeer', -21.2, NAVY),
    ('Cango (est.)', -63.2, RED),
]
labels, values, colors = zip(*items)
y = np.arange(len(items))

fig, ax = plt.subplots(figsize=(12.4, 5.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')


def grad_bar(ax, yi, h, v, color, floor=0.68):
    """0 쪽이 어둡고 막대 끝으로 갈수록 밝아지는 가로 그라데이션 막대."""
    r, g, b = mcolors.to_rgb(color)
    f = floor + (1 - floor) * np.linspace(0, 1, 256) ** 0.5
    if v < 0:                       # 왼쪽으로 자라는 막대는 좌우를 뒤집는다
        f = f[::-1]
    grad = np.stack([r * f, g * f, b * f, np.ones(256)], axis=-1)[None, :, :]
    ax.imshow(grad, aspect='auto', origin='lower', interpolation='bilinear',
              extent=[min(0, v), max(0, v), yi - h / 2, yi + h / 2], zorder=3)


for yi, v, col in zip(y, values, colors):
    grad_bar(ax, yi, 0.58, v, col)
    ax.annotate(f'{v:+.1f}%', xy=(v, yi), xytext=(10 if v >= 0 else -10, 0),
                textcoords='offset points', ha='left' if v >= 0 else 'right',
                va='center', fontsize=14, fontweight='bold',
                color=col if col in (TEAL, RED) else COLORS['text'], zorder=5)

ax.set_xlim(-75, 75)
ax.set_ylim(len(items) - 0.5, -0.5)   # imshow가 축을 이미지에 맞추므로 여백 복구
ticks = [-60, -40, -20, 0, 20, 40, 60]
ax.set_xticks(ticks)
ax.set_xticklabels([f'{t}%' for t in ticks], fontweight='bold')
ax.set_yticks(y)
ax.set_yticklabels(labels, fontweight='bold')

ax.axvline(0, color=COLORS['text'], linewidth=1.2, zorder=4)
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
print(save_chart(fig, 'realized_hashrate_change',
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
