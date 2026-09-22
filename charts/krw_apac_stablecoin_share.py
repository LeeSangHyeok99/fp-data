import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/krw_apac_stablecoin_share.csv')
labels = df['currency'].tolist()
values = df['share'].tolist()

colors = ['#1f3a8a', '#6aa3ff']

setup_font()
fig, ax = plt.subplots(figsize=(970/150, 970/150), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

wedges, texts, autotexts = ax.pie(
    values,
    labels=None,
    autopct=lambda pct: f'{pct:.1f}%',
    startangle=90,
    counterclock=False,
    colors=colors,
    wedgeprops=dict(edgecolor='#141414', linewidth=2),
    pctdistance=0.72,
    textprops=dict(color='#ffffff', fontsize=16, fontweight='bold'),
)

for autotext in autotexts:
    autotext.set_fontsize(16)
    autotext.set_fontweight('bold')
    autotext.set_color('#ffffff')

for wedge, label in zip(wedges, labels):
    angle = (wedge.theta2 + wedge.theta1) / 2
    import math
    x = 1.15 * math.cos(math.radians(angle))
    y = 1.15 * math.sin(math.radians(angle))
    ha = 'left' if x >= 0 else 'right'
    ax.text(x, y, label, ha=ha, va='center',
            fontsize=16, fontweight='bold', color=COLORS['text_secondary'])

ax.set_aspect('equal')

output_dir = 'outputs/charts/stablecoin/apac'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f'{output_dir}/krw_apac_stablecoin_share.png'
svg_path = f'{output_dir}/krw_apac_stablecoin_share.svg'

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Saved: {png_path}")
