import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/markets_xyz_market_share_volume.csv')
df = df[df['share_pct'] > 0].reset_index(drop=True)

# Keep top 4 (US500, USTECH, SILVER, USOIL); group SMALL2000 and below as Others
KEEP = ['US500', 'USTECH', 'SILVER', 'USOIL']
big = df[df['ticker'].isin(KEEP)].copy()
small = df[~df['ticker'].isin(KEEP)]
if len(small) > 0:
    others_row = pd.DataFrame([{
        'ticker': 'Others',
        'category': 'Mixed',
        'share_pct': small['share_pct'].sum(),
        'volume_usd': small['volume_usd'].sum(),
    }])
    big = pd.concat([big, others_row], ignore_index=True)

labels = big['ticker'].tolist()
values = big['share_pct'].tolist()

# Color palette: index=blue family, commodity=gold/silver, single stocks=warm/cool accents
color_map = {
    'US500':     '#5470c6',
    'USTECH':    '#73c0de',
    'SILVER':    '#c0c0cc',
    'USOIL':     '#b5651d',
    'SMALL2000': '#9a60b4',
    'TSLA':      '#ee6666',
    'GOLD':      '#e8b008',
    'NVDA':      '#91cc75',
    'BABA':      '#fc8452',
    'USBOND':    '#3b6ea8',
    'GOOGL':     '#fac858',
    'Others':    '#555c66',
}
colors = [color_map.get(l, '#555c66') for l in labels]

setup_font()
fig, ax = plt.subplots(figsize=(970/150, 970/150), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

wedges, texts, autotexts = ax.pie(
    values,
    labels=None,
    autopct=lambda pct: f'{pct:.1f}%' if pct >= 3 else '',
    startangle=90,
    counterclock=False,
    colors=colors,
    wedgeprops=dict(width=0.42, edgecolor='#141414', linewidth=2),
    pctdistance=0.80,
    textprops=dict(color='#ffffff', fontsize=13, fontweight='bold'),
)

for autotext in autotexts:
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')
    autotext.set_color('#ffffff')

# External labels for the larger wedges
for w, lbl, val in zip(wedges, labels, values):
    if val < 3:
        continue
    ang = (w.theta2 + w.theta1) / 2.0
    x = np.cos(np.deg2rad(ang)) * 1.08
    y = np.sin(np.deg2rad(ang)) * 1.08
    ha = 'left' if x >= 0 else 'right'
    ax.text(x, y, lbl, ha=ha, va='center',
            fontsize=13, fontweight='bold', color=COLORS['text'])

ax.set_aspect('equal')
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.35, 1.35)

output_dir = 'outputs/charts/markets_xyz/volume'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f'{output_dir}/markets_xyz_market_share_volume.png'
svg_path = f'{output_dir}/markets_xyz_market_share_volume.svg'

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
print(f"\n--- Market Share (Volume, Last 12M) ---")
total = sum(values)
for l, v in zip(labels, values):
    print(f"  {l}: {v:.1f}%")
print(f"  Total: {total:.1f}% of $2.96B")
