import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, gradient_barh, COLORS

df = pd.read_csv('outputs/data/kalshi_turnover_vs_corn.csv')

labels = df['category'].tolist()
# split "Name (detail)" into a bold main line and a lighter, smaller detail line
label_parts = []
for l in labels:
    name, _, detail = l.partition(' (')
    label_parts.append((name, f'({detail}' if detail else None))
values = df['turnover'].tolist()

bar_colors = ['#ee6666', '#91cc75', '#5470c6']  # Kalshi Sports, Corn, Kalshi Weather

fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(11.5, 4.67)

y = range(len(labels))
bars = ax.barh(list(y), values, height=0.55, color=bar_colors, zorder=3)

for rect, c in zip(bars, bar_colors):
    gradient_barh(ax, rect, c)

# Value labels at bar end
for rect, v in zip(bars, values):
    ax.text(v + 0.012, rect.get_y() + rect.get_height() / 2, f'{v:.3f}',
            va='center', ha='left', fontsize=20, fontweight='bold',
            color=COLORS['text'], zorder=4)

ax.set_yticks(list(y))
ax.set_yticklabels([])
ax.tick_params(axis='y', length=0)
ax.invert_yaxis()
# 그라데이션 imshow가 y축을 이미지 경계에 딱 맞춰버려서 맨 위 막대가 잘린다.
# 막대 반높이(0.275)보다 넉넉한 범주형 기본 여백으로 되돌린다.
ax.set_ylim(len(labels) - 0.5, -0.5)

# manual two-line y labels: bold category name, lighter detail line below
# (axis is inverted, so a *smaller* y offset lands visually higher)
for rect, (name, detail) in zip(bars, label_parts):
    yc = rect.get_y() + rect.get_height() / 2
    if detail:
        ax.text(-0.015, yc - 0.11, name, transform=ax.get_yaxis_transform(),
                 ha='right', va='center', fontsize=17, fontweight='bold',
                 color=COLORS['text_secondary'], clip_on=False)
        ax.text(-0.015, yc + 0.13, detail, transform=ax.get_yaxis_transform(),
                 ha='right', va='center', fontsize=13, fontweight='bold',
                 color=COLORS['text_secondary'], clip_on=False)
    else:
        ax.text(-0.015, yc, name, transform=ax.get_yaxis_transform(),
                 ha='right', va='center', fontsize=17, fontweight='bold',
                 color=COLORS['text_secondary'], clip_on=False)

ax.set_xlim(0, 0.4)
ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
ax.set_xticklabels(['0', '0.1', '0.2', '0.3', '0.4'])

ax.set_xlabel('Daily Turnover (Volume / Open Interest)', fontsize=17,
              fontweight='bold', color=COLORS['text_secondary'], labelpad=14)

apply_style(fig, ax, 'horizontal_bar')

# horizontal bar needs vertical gridlines instead of the default horizontal ones
ax.grid(False, axis='y')
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# x-axis is a plain numeric scale here, no need for the default 45-degree rotation
ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/kalshi/turnover').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'kalshi_turnover_vs_corn', 'outputs/charts/kalshi/turnover')
plt.close(fig)

print(png_path)
print(svg_path)
