import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, gradient_barh, COLORS

df = pd.read_csv('outputs/data/kalshi_hold_to_expiry.csv')

labels = df['category'].tolist()
labels = [l.replace(' · ', '\n') for l in labels]
values = df['ratio'].tolist()
contracts = df['contracts'].tolist()

bar_colors = ['#99b7dc', '#3f6cb0', '#dea39c', '#af5954']  # Weather >45d/3-45d, Sports >45d/3-45d

fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(11.5, 4.67)

y = range(len(labels))
bars = ax.barh(list(y), values, height=0.55, color=bar_colors, zorder=3)

for rect, c in zip(bars, bar_colors):
    gradient_barh(ax, rect, c)

# Value + contract count labels at bar end
for rect, v, n in zip(bars, values, contracts):
    ax.text(v + 0.012, rect.get_y() + rect.get_height() / 2,
            f'{v:.3f}\n({n} Contracts)',
            va='center', ha='left', fontsize=16, fontweight='bold',
            color=COLORS['text'], zorder=4, linespacing=1.3)

ax.set_yticks(list(y))
ax.set_yticklabels(labels)
ax.invert_yaxis()
# 그라데이션 imshow가 y축을 이미지 경계에 딱 맞춰버려서 맨 위 막대가 잘린다.
# 막대 반높이(0.275)보다 넉넉한 범주형 기본 여백으로 되돌린다.
ax.set_ylim(len(labels) - 0.5, -0.5)

ax.set_xlim(0, 0.65)
ax.set_xticks([0, 0.2, 0.4, 0.6])
ax.set_xticklabels(['0', '0.2', '0.4', '0.6'])

ax.set_xlabel('Hold-To-Expiry Ratio (OI At Expiry / Cumulative Volume)',
              fontsize=17, fontweight='bold', color=COLORS['text_secondary'],
              labelpad=14)

apply_style(fig, ax, 'horizontal_bar')

ax.tick_params(axis='y', labelsize=17)

# horizontal bar needs vertical gridlines instead of the default horizontal ones
ax.grid(False, axis='y')
ax.grid(False, axis='x')
for gx in [0.2, 0.4, 0.6]:
    ax.axvline(gx, color=COLORS['grid'], alpha=0.5,
               linestyle=(0, (3.7, 1.6)), linewidth=1.0, zorder=1)
ax.set_axisbelow(True)

# x-axis is a plain numeric scale here, no need for the default 45-degree rotation
ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/kalshi/hold_to_expiry').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'kalshi_hold_to_expiry', 'outputs/charts/kalshi/hold_to_expiry')
plt.close(fig)

print(png_path)
print(svg_path)
