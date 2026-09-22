import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

TOKEN_COLOR = {
    'WEETH': '#29CBE9',
    'WSTETH': '#00A3FF',
    'RSETH': '#5B61FE',
    'OSETH': '#00D2E9',
    'EZETH': '#1E2DB3',
    'WRSETH': '#7F61EF',
    'WBTC': '#F09242',
    'CBBTC': '#0052FF',
    'LBTC': '#FFCB45',
    'TBTCV2': '#54478C',
    'BTC.B': '#E84142',
    'SUSDE': '#8854D0',
    'USDE': '#D26AEB',
    'PT-SUSDE-18JUN2026': '#00C2B6',
    'SYRUPUSDT': '#FF007A',
    'Others': '#6B7280',
}

TOKEN_FAMILY = {
    'WEETH': 'lst', 'WSTETH': 'lst', 'RSETH': 'lst', 'OSETH': 'lst',
    'EZETH': 'lst', 'WRSETH': 'lst',
    'WBTC': 'btc', 'CBBTC': 'btc', 'LBTC': 'btc', 'TBTCV2': 'btc', 'BTC.B': 'btc',
    'SUSDE': 'ethena', 'USDE': 'ethena', 'PT-SUSDE-18JUN2026': 'ethena',
    'SYRUPUSDT': 'stable',
    'Others': 'other',
}

df = pd.read_csv('outputs/data/aave_v3_tokens_breakdown.csv')

MIN_SHARE = 5.0
keep = df[(df['share_pct'] >= MIN_SHARE) & (df['token'] != 'Others')].copy()
small = df[(df['share_pct'] < MIN_SHARE) & (df['token'] != 'Others')].copy()
others_row = df[df['token'] == 'Others']
others_total = (others_row['share_pct'].sum() if not others_row.empty else 0.0) + small['share_pct'].sum()

keep = keep.sort_values('share_pct', ascending=False).reset_index(drop=True)
merged = pd.concat([
    keep,
    pd.DataFrame([{'token': 'Others', 'share_pct': others_total}]),
], ignore_index=True)

labels = merged['token'].tolist()
values = merged['share_pct'].tolist()
colors = [TOKEN_COLOR.get(t, '#6B7280') for t in labels]
total = sum(values)

setup_font()
fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

wedges, _ = ax.pie(
    values,
    labels=None,
    startangle=90,
    counterclock=False,
    colors=colors,
    wedgeprops=dict(width=0.55, edgecolor='#141414', linewidth=2),
)

for w, v, lab in zip(wedges, values, labels):
    pct = v / total * 100
    angle = (w.theta2 + w.theta1) / 2
    if pct >= 5:
        r = 0.72
        x = np.cos(np.radians(angle)) * r
        y = np.sin(np.radians(angle)) * r
        ax.text(x, y, f'{lab}\n{pct:.1f}%',
                ha='center', va='center',
                fontsize=11, color='#ffffff', fontweight='bold')
    elif pct >= 2:
        r = 1.12
        x = np.cos(np.radians(angle)) * r
        y = np.sin(np.radians(angle)) * r
        ha = 'left' if x >= 0 else 'right'
        ax.text(x, y, f'{lab} {pct:.1f}%',
                ha=ha, va='center',
                fontsize=9.5, color=COLORS['text'], fontweight='bold')

ax.set_aspect('equal')
ax.set_xlim(-1.8, 1.8)
ax.set_ylim(-1.25, 1.25)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

output_dir = 'outputs/charts/aave/tvl'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f'{output_dir}/aave_v3_tokens_breakdown.png'
svg_path = f'{output_dir}/aave_v3_tokens_breakdown.svg'

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', transparent=True)
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

print("\n--- Chart slices (>=3% + rolled Others) ---")
for lab, v in zip(merged['token'], merged['share_pct']):
    print(f"  {lab:<22} {v:>6.2f}%")
print(f"  {'Total':<22} {total:>6.2f}%")

print("\n--- Rolled into Others ---")
for lab, v in zip(small['token'], small['share_pct']):
    print(f"  {lab:<22} {v:>6.2f}%")
print(f"  {'DefiLlama Others':<22} {others_row['share_pct'].sum():>6.2f}%" if not others_row.empty else "")

family_totals = {}
for lab, v in zip(df['token'], df['share_pct']):
    fam = TOKEN_FAMILY.get(lab, 'other')
    family_totals[fam] = family_totals.get(fam, 0) + v
print("\n--- Family totals (full dataset) ---")
for fam, tot in sorted(family_totals.items(), key=lambda x: -x[1]):
    print(f"  {fam:<8} {tot:>6.2f}%")
