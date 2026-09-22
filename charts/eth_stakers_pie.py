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

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/Stakers.csv')

top5 = ['Kraken', 'ether.fi', 'Binance', 'Lido', 'Mantle']
top5_df = df[df['entity'].isin(top5)].set_index('entity').loc[top5]
others_val = df[~df['entity'].isin(top5)]['validators'].sum()

labels = list(top5) + ['Others']
values = list(top5_df['validators'].values) + [others_val]
total = sum(values)

# 브랜드 컬러
brand_colors = {
    'Kraken':    '#5741D9',
    'ether.fi':  '#2ECBE9',
    'Binance':   '#F0B90B',
    'Lido':      '#00A3FF',
    'Mantle':    '#65D886',
    'Others':    '#555555',
}
colors = [brand_colors[l] for l in labels]

# =============================================================================
# 파이 차트
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(970/150, 970/150), dpi=150)

fig.patch.set_alpha(0)
ax.set_facecolor('none')

wedges, texts, autotexts = ax.pie(
    values,
    labels=None,
    autopct=lambda pct: f'{pct:.1f}%' if pct >= 3 else '',
    startangle=90,
    colors=colors,
    wedgeprops=dict(width=0.55, edgecolor='#141414', linewidth=2),
    pctdistance=0.75,
    textprops=dict(color=COLORS['text'], fontsize=16, fontweight='bold'),
)

for autotext in autotexts:
    autotext.set_fontsize(14)
    autotext.set_fontweight('bold')
    autotext.set_color('#ffffff')

ax.set_aspect('equal')

# =============================================================================
# 저장
# =============================================================================
output_dir = 'outputs/charts/stakers'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f'{output_dir}/eth_stakers_pie.png'
svg_path = f'{output_dir}/eth_stakers_pie.svg'

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# 통계
print(f"\n--- Staker Distribution ---")
for l, v in zip(labels, values):
    print(f"  {l}: {v:,} validators ({v/total*100:.1f}%)")
print(f"  Total: {total:,}")
