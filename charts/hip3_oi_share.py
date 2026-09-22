import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, save_chart, SERIES_COLORS, COLORS

# ══════════════════════════════════════════════════
# Data (Google Sheet, 2026-02-09)
# ══════════════════════════════════════════════════
deployers = ['XYZ', 'HyENA OI', 'Markets OI', 'Cash', 'FLX', 'VNTL']
oi_raw = [628257364, 43905110, 15720104, 32012201, 10781538, 7317280]
total_oi = sum(oi_raw)
shares = [v / total_oi * 100 for v in oi_raw]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=150)

# Bar colors - match reference image order
bar_colors = [SERIES_COLORS[0], SERIES_COLORS[2], SERIES_COLORS[3],
              SERIES_COLORS[1], SERIES_COLORS[4], SERIES_COLORS[5]]

x = np.arange(len(deployers))
bars = ax.bar(x, shares, width=0.5, color=bar_colors, edgecolor='none', zorder=3)

# Value labels
for bar, share in zip(bars, shares):
    if share > 10:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 3,
                f'{share:.1f}%', ha='center', va='top',
                fontsize=14, fontweight='bold', color='#ffffff')
    elif share > 3:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{share:.1f}%', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=COLORS['text'])

# ══════════════════════════════════════════════════
# Axes
# ══════════════════════════════════════════════════
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}%'))

ax.set_xticks(x)
ax.set_xticklabels(deployers)

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
apply_style(fig, ax, 'bar')

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'hip3_oi_share', 'outputs/charts/hyperliquid')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
