"""
Tokenized Treasury League Table - Horizontal Bar Chart (Gradient)
Data source: RWA.xyz (app.rwa.xyz) - Tokenized Treasury, Platforms
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

# Font
pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    pretendard_font = fm.FontProperties(fname=str(pretendard_path))
else:
    pretendard_font = None

# ─── Gradient bar helper ───────────────────────────────────────────────
def gradient_hbar(ax, y_center, width, height, color):
    from matplotlib.patches import Rectangle
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.25 + 0.75 * (frac ** 0.5)
        gradient[0, i] = [r * factor, g * factor, b * factor, 1.0]
    x0, x1 = 0, width
    y0, y1 = y_center - height / 2, y_center + height / 2
    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x0, x1, y0, y1], zorder=3, interpolation='bicubic')
    clip_rect = Rectangle((x0, y0), width, height, transform=ax.transData)
    im.set_clip_path(clip_rect)


# ─── Data (RWA.xyz Tokenized Treasury League Table, 2026-04-10) ───────
data = [
    ('Circle',                   2700,  32.14, 20.16, '#2775ca'),
    ('Ondo',                     2600,  23.34, 19.54, '#1a1a2e'),
    ('Securitize',               2400,  17.22, 18.45, '#5470c6'),
    ('Centrifuge',               1300, 124.50,  9.61, '#f0b90b'),
    ('Franklin Templeton',       1000,  -1.96,  7.70, '#003087'),
    ('Libeara',                   873,   4.83,  6.60, '#3ba272'),
    ('WisdomTree',                861,  10.27,  6.51, '#73c0de'),
    ('Superstate',                644,   4.25,  4.87, '#9a60b4'),
    ('Spiko',                     156, -17.98,  1.18, '#ee6666'),
    ('Theo',                      133,   0.26,  1.00, '#fc8452'),
]

# Reverse for bar chart (top at top)
data = data[::-1]
names = [d[0] for d in data]
values = [d[1] for d in data]  # in millions
pct_30d = [d[2] for d in data]
shares = [d[3] for d in data]
colors = [d[4] for d in data]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('horizontal_bar')

bar_height = 0.6
for i, (name, val, color) in enumerate(zip(names, values, colors)):
    gradient_hbar(ax, i, val, bar_height, color)

# Value labels
for i, (name, val, share) in enumerate(zip(names, values, shares)):
    if val >= 1000:
        label = f'${val/1000:.1f}B ({share:.1f}%)'
    else:
        label = f'${val:.0f}M ({share:.1f}%)'
    ax.text(val + 20, i, label, va='center', ha='left',
            fontsize=13, fontweight='bold', color=COLORS['text'],
            fontproperties=pretendard_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=15, fontweight='bold',
                   color=COLORS['text'], fontproperties=pretendard_font)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.tick_params(axis='x', labelsize=0, length=0)
ax.set_xticklabels([])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'horizontal_bar')
ax.grid(False)
ax.tick_params(axis='y', length=0, pad=10)
ax.set_xlim(0, max(values) * 1.45)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/rwa/treasury'
png_path, svg_path = save_chart(fig, 'tokenized_treasury_league', output_dir)
plt.close()
print(f'Saved: {png_path}')
