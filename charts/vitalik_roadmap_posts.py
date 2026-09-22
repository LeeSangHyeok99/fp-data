import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (setup_font, apply_style, save_chart, COLORS,
                    SERIES_COLORS, GRID_CONFIG, DPI, gradient_rounded_bar)

mpl.rcParams['axes.unicode_minus'] = False

# --labels: Y축(틱/그리드) 없이 바 위에 값만 얹는 버전
LABELS = '--labels' in sys.argv

df = pd.read_csv('/Users/a./Downloads/vitalik-roadmap-chart.csv')
x = range(len(df))

BLUE = SERIES_COLORS[0]

# 마일스톤 라벨은 바 위에 2줄로 (긴 것만 줄바꿈)
WRAP = {
    'Rollup-centric roadmap': 'Rollup-Centric\nRoadmap',
    'The Merge': 'The Merge',
    'Devcon Beam chain': 'Devcon\nBeam Chain',
    'Lean Ethereum': 'Lean\nEthereum',
    'Strawmap': 'Strawmap',
}

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)

ax.set_ylim(0, 12.4 if LABELS else 11.6)
ax.set_yticks([] if LABELS else [0, 2, 4, 6, 8])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}'))

ax.set_xticks(list(x))
ax.set_xticklabels([str(y).replace(' (', '\n(') for y in df['Year']])
ax.set_xlim(-0.7, len(df) - 0.3)

for xi, v in zip(x, df['Posts']):
    gradient_rounded_bar(ax, x_center=xi, width=0.52, height=v,
                         color=BLUE, floor=0.55, round_top=False)

if LABELS:
    for xi, v in zip(x, df['Posts']):
        ax.text(xi, v - 0.28, f'{v:.0f}', ha='center', va='top',
                fontsize=17, fontweight='bold', color='#ffffff', zorder=6)

for xi, v, m in zip(x, df['Posts'], df['Milestone']):
    if pd.isna(m):
        continue
    ax.text(xi, v + 0.35, WRAP[m], ha='center', va='bottom',
            fontsize=14, fontweight='bold', color=COLORS['text'],
            linespacing=1.25, zorder=6)

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=18, length=0,
               colors=COLORS['text_secondary'], pad=12)
ax.tick_params(axis='x', labelsize=15, length=0,
               colors=COLORS['text_secondary'], pad=10, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

if LABELS:
    ax.grid(False)
else:
    ax.grid(True, axis='y',
            color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
fig.tight_layout()

out = 'outputs/charts/ethereum/roadmap'
Path(out).mkdir(parents=True, exist_ok=True)
png, svg = save_chart(
    fig, 'vitalik_roadmap_posts' + ('_labeled' if LABELS else ''), out)
plt.close(fig)
print(png, svg)
