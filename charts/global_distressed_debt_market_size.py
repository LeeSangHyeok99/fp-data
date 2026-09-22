import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    setup_font, apply_style, COLORS, GRID_CONFIG, DPI,
    gradient_rounded_bar,
)

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/distressed_debt_market_size.csv')

setup_font()
fm.fontManager.addfont('assets/font/Pretendard/Pretendard-Medium.ttf')
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['font.weight'] = 'medium'
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

BAR_COLOR = '#91cc75'

x = np.arange(len(df))
bar_width = 0.6

for xi, v in zip(x, df['value']):
    gradient_rounded_bar(ax, x_center=xi, width=bar_width, height=v, color=BAR_COLOR)
    ax.text(xi, v + 8, f'${v:.1f}M', ha='center', va='bottom',
            fontsize=11, fontweight='medium', color=COLORS['text'])

ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str).tolist())
ax.set_xlim(-0.7, len(df) - 0.3)

ax.set_ylim(0, 450)
ax.set_yticks([0, 100, 200, 300, 400])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=16, length=0)
ax.tick_params(axis='x', labelsize=14, length=0, pad=10, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('medium')

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/macro/distressed_debt'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/global_distressed_debt_market_size.png"
svg_path = f"{output_dir}/global_distressed_debt_market_size.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
