import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data (Sealaunch / DefiLlama, categories with >$5M 30d rev)
# ══════════════════════════════════════════════════
df = pd.read_csv('outputs/data/sealaunch_leader_share.csv')
df = df.sort_values('leader_share', ascending=True)

categories = df['category'].values
shares = df['leader_share'].values

# ══════════════════════════════════════════════════
# Color: gradient from distributed (blue) to concentrated (red)
# ══════════════════════════════════════════════════
def share_to_color(s):
    # Blue (#5470c6) for low share, Red (#E07B7B) for high share
    t = (s - 20) / 80  # normalize roughly 20-100 range
    t = max(0, min(1, t))
    r = int(0x54 + (0xE0 - 0x54) * t)
    g = int(0x70 + (0x7B - 0x70) * t)
    b = int(0xC6 + (0x7B - 0xC6) * t)
    return f'#{r:02x}{g:02x}{b:02x}'

bar_colors = [share_to_color(s) for s in shares]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(13.33, 6.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Horizontal bars
# ══════════════════════════════════════════════════
y_pos = np.arange(len(categories))
bars = ax.barh(y_pos, shares, height=0.65, color=bar_colors, edgecolor='none')

# Add percentage labels at end of each bar
for i, (bar, share) in enumerate(zip(bars, shares)):
    ax.text(share + 1.5, bar.get_y() + bar.get_height() / 2,
            f'{share}%', va='center', ha='left',
            fontsize=15, fontweight='bold',
            color=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# Median line
# ══════════════════════════════════════════════════

# ══════════════════════════════════════════════════
# Axes
# ══════════════════════════════════════════════════
ax.set_yticks(y_pos)
ax.set_yticklabels(categories)
ax.set_xlim(0, 110)
ax.set_xticks([0, 25, 50, 75, 100])
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=16, pad=10, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=15, pad=10, length=0,
               colors=COLORS['text_secondary'])

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'crypto_revenue_leader_share',
                                'outputs/charts/crypto-revenue')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
