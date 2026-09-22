import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch
import numpy as np
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    setup_font, apply_style, COLORS, GRID_CONFIG, DPI,
    gradient_rounded_bar,
)

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/tcg_market_size.csv')

setup_font()
fm.fontManager.addfont('assets/font/Pretendard/Pretendard-Medium.ttf')
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['font.weight'] = 'medium'

fig, ax = plt.subplots(figsize=(10.67, 6.8), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

BAR_COLOR = '#8098e8'
ARROW_COLOR = '#73c0de'

x = np.array([0.0, 0.6, 2.5])
bar_width = 0.28

for xi, v in zip(x, df['value']):
    gradient_rounded_bar(ax, x_center=xi, width=bar_width, height=v, color=BAR_COLOR)
    ax.text(xi, v + 1.0, f'${v:.2f}B', ha='center', va='bottom',
            fontsize=18, fontweight='medium', color=COLORS['text'],
            fontfamily='Pretendard')

ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str).tolist())
ax.set_xlim(-0.55, x[-1] + 0.55)

ax.set_ylim(0, 40)
ax.set_yticks([0, 10, 20, 30, 40])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))

x_start = x[1] + bar_width / 2 + 0.05
y_start = df['value'].iloc[1] + 1.5
x_end = x[2] - bar_width / 2 - 0.02
y_end = df['value'].iloc[2] + 0.4

arrow = FancyArrowPatch(
    (x_start, y_start), (x_end, y_end),
    arrowstyle='->,head_length=10,head_width=7',
    color=ARROW_COLOR, linewidth=2.2, zorder=4,
)
ax.add_patch(arrow)

mid_x = (x_start + x_end) / 2
mid_y = (y_start + y_end) / 2
ax.text(mid_x, mid_y + 4.2, 'CAGR', ha='center', va='bottom',
        fontsize=14, fontweight='medium', color=COLORS['text_secondary'])
ax.text(mid_x, mid_y + 1.8, '10.03%', ha='center', va='bottom',
        fontsize=18, fontweight='bold', color=ARROW_COLOR)

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=16, length=0)
ax.tick_params(axis='x', labelsize=16, length=0, pad=12, rotation=0, colors=COLORS['text'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('medium')

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/macro/tcg'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/tcg_market_size.png"
svg_path = f"{output_dir}/tcg_market_size.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
