import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data (Noodles API, timeframe=all, 2026-03-05)
# ══════════════════════════════════════════════════
coins = [
    ('USDSUI',   5.0,    0.96,   1.4),
    ('suiUSDe',  12.5,   1.2,    2.4),
    ('USDY',     17.3,   0.17,   3.7),
    ('AUSD',     21.0,   0.001,  0.25),
    ('BUCK',     35.2,   1.5,    4.4),
    ('USDB',     35.2,   2.2,    5.6),
    ('suiUSDT',  49.5,   67.8,   11.0),
    ('FDUSD',    63.7,   0.62,   0.11),
    ('USDC',     476.4,  124.3,  62.6),
]

names = [c[0] for c in coins]
mcaps = [c[1] for c in coins]

# Colors: USDSUI gets Sui blue, others get sequential palette
color_map = {
    'USDC':     '#2775CA',
    'suiUSDT':  '#50AF95',
    'FDUSD':    '#E8B84B',
    'USDB':     '#9a60b4',
    'BUCK':     '#ea7ccc',
    'AUSD':     '#73c0de',
    'USDY':     '#fc8452',
    'suiUSDe':  '#3ba272',
    'USDSUI':   '#4DA2FF',  # Sui brand blue
}
bar_colors = [color_map[n] for n in names]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=150)

y_pos = np.arange(len(names))
bars = ax.barh(y_pos, mcaps, height=0.6, color=bar_colors, alpha=0.9,
               edgecolor='#1a1a1a', linewidth=0.5)

# Value labels
for i, (name, val) in enumerate(zip(names, mcaps)):
    if val > 30:
        ax.text(val - 2, i, f'${val:.0f}M', ha='right', va='center',
                color='white', fontsize=11, fontweight='bold')
    else:
        ax.text(val + 3, i, f'${val:.1f}M', ha='left', va='center',
                color=COLORS['text'], fontsize=11, fontweight='bold')

# ══════════════════════════════════════════════════
# Axes
# ══════════════════════════════════════════════════
ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=13, fontweight='bold', color=COLORS['text'])
ax.set_xlim(0, 520)
ax.set_xticks([0, 100, 200, 300, 400, 500])
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'${int(x)}M'))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Grid on x-axis only
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0)

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'sui_stablecoin_bar',
                                'outputs/charts/sui')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
