import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

# ── Data (share of all hackathon submissions, %) ──
df = pd.read_csv('outputs/data/hackathon_sector_share.csv').set_index('sector')
years = list(df.columns)

# ── Stacking order: bottom → top (reference palette: AI orange, rest gray ramp) ──
sectors = [
    ('AI & Agents',            '#ee7a2a'),
    ('Payments & Commerce',    '#c8c8c8'),
    ('Consumer Apps & Gaming', '#a3a3a3'),
    ('DeFi & Tokenization',    '#808080'),
    ('Infrastructure & Trust', '#5c5c5c'),
    ('Other / Unclear',        '#3d3d3d'),
]

fig, ax = create_figure('stacked_bar')
fig.set_size_inches(10.67, 5.6)  # 세로로 길게 (라벨 여유)

x = np.arange(len(years))
bar_width = 0.62

bottom = np.zeros(len(years))
for name, color in sectors:
    v = df.loc[name, years].values.astype(float)
    ax.bar(x, v, bar_width, bottom=bottom, color=color,
           edgecolor=COLORS['background'], linewidth=0.8)
    bottom += v

# ── % labels on the AI & Agents band (reference behaviour) ──
ai = df.loc['AI & Agents', years].values.astype(float)
for xi, v in zip(x, ai):
    if v >= 12:  # band tall enough to hold the label
        ax.text(xi, v / 2, f'{v:.1f}%', ha='center', va='center',
                fontsize=17, fontweight='bold', color='#ffffff')
    else:
        ax.text(xi, v + 1.5, f'{v:.1f}%', ha='center', va='bottom',
                fontsize=17, fontweight='bold', color='#ee7a2a')

ax.set_xticks(x)
ax.set_xticklabels(years)
ax.set_xlim(-0.45, len(years) - 1 + 0.45)

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=18)
ax.tick_params(axis='x', labelsize=18, length=6, width=1,
               color=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center',
         fontweight='bold')
fig.tight_layout()

png_path, svg_path = save_chart(fig, 'hackathon_sector_share_stacked_bar',
                                'outputs/charts/hackathon/sector')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
