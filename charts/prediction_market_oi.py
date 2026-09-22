import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (setup_font, COLORS, DPI, GRID_CONFIG,
                    gradient_rounded_bar)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/prediction_market_oi.csv')

output_dir = 'outputs/charts/prediction_markets'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Chart 1: Category OI Distribution (Horizontal Bar)
# =============================================================================
setup_font()

cat_oi = df.groupby('category')['open_interest_usd'].sum().sort_values()
cat_oi_m = cat_oi / 1e6  # Convert to millions

# Colors per category
cat_colors = {
    'STEM': '#9a60b4',
    'Culture': '#ea7ccc',
    'Financials': '#fac858',
    'Crypto': '#f7931a',
    'Economics': '#73c0de',
    'Sports': '#91cc75',
    'Politics': '#5470c6',
}

colors = [cat_colors.get(c, '#888888') for c in cat_oi.index]

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bars = ax.barh(range(len(cat_oi_m)), cat_oi_m.values, height=0.55,
               color=colors, alpha=0.9, edgecolor='#1a1a1a', linewidth=0.5)

# Category labels on y-axis
ax.set_yticks(range(len(cat_oi_m)))
ax.set_yticklabels(cat_oi_m.index, fontsize=13, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# Value labels on bars
for i, (val, color) in enumerate(zip(cat_oi_m.values, colors)):
    ax.text(val + 2, i, f'${val:.0f}M', va='center', ha='left',
            fontsize=11, fontweight='bold', color=color)

# X-axis
x_ticks = [0, 50, 100, 150, 200, 250]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}M' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, 280)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_oi_by_category.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_oi_by_category.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 1 saved: Category OI Distribution")
print(f"  Total OI: ${cat_oi.sum()/1e6:.0f}M")
for c in cat_oi.sort_values(ascending=False).index:
    pct = cat_oi[c] / cat_oi.sum() * 100
    print(f"  {c}: ${cat_oi[c]/1e6:.0f}M ({pct:.1f}%)")

# =============================================================================
# Chart 2: Kalshi vs Polymarket by Category (Grouped Bar)
# =============================================================================
setup_font()

pivot = df.groupby(['category', 'source'])['open_interest_usd'].sum().unstack(fill_value=0)
pivot = pivot / 1e6
# Sort by total
pivot['total'] = pivot.sum(axis=1)
pivot = pivot.sort_values('total', ascending=True)
pivot = pivot.drop('total', axis=1)

KALSHI_C = '#5470c6'
POLY_C = '#91cc75'

fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = np.arange(len(pivot))
bar_h = 0.35

kalshi_vals = pivot.get('Kalshi', pd.Series(0, index=pivot.index)).values
poly_vals = pivot.get('Polymarket', pd.Series(0, index=pivot.index)).values

bars1 = ax.barh(y + bar_h/2, kalshi_vals, bar_h, color=KALSHI_C, alpha=0.9,
                edgecolor='#1a1a1a', linewidth=0.5)
bars2 = ax.barh(y - bar_h/2, poly_vals, bar_h, color=POLY_C, alpha=0.9,
                edgecolor='#1a1a1a', linewidth=0.5)

# Value labels
for i in range(len(pivot)):
    if kalshi_vals[i] > 3:
        ax.text(kalshi_vals[i] + 1.5, y[i] + bar_h/2, f'${kalshi_vals[i]:.0f}M',
                va='center', ha='left', fontsize=9, fontweight='bold', color=KALSHI_C)
    if poly_vals[i] > 3:
        ax.text(poly_vals[i] + 1.5, y[i] - bar_h/2, f'${poly_vals[i]:.0f}M',
                va='center', ha='left', fontsize=9, fontweight='bold', color=POLY_C)

# Y-axis
ax.set_yticks(y)
ax.set_yticklabels(pivot.index, fontsize=13, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
x_ticks = [0, 50, 100, 150]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}M' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, 170)

# Platform labels (top-right, instead of legend)
ax.text(0.97, 0.97, 'Kalshi', transform=ax.transAxes, ha='right', va='top',
        fontsize=12, fontweight='bold', color=KALSHI_C)
ax.text(0.97, 0.90, 'Polymarket', transform=ax.transAxes, ha='right', va='top',
        fontsize=12, fontweight='bold', color=POLY_C)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_oi.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_oi.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("\nChart 2 saved: Kalshi vs Polymarket")

# =============================================================================
# Chart 3: Top Markets by Volume/OI Ratio (Activity)
# =============================================================================
setup_font()

# Merge same subsubcategory across platforms
merged = df.groupby('subsubcategory').agg({
    'volume_usd': 'sum',
    'open_interest_usd': 'sum',
    'category': 'first'
}).reset_index()
merged['vol_oi_ratio'] = merged['volume_usd'] / merged['open_interest_usd']
merged = merged[merged['open_interest_usd'] > 3_000_000]  # Min $3M OI
merged = merged.sort_values('vol_oi_ratio', ascending=True).tail(12)

# Color by category
bar_colors = [cat_colors.get(c, '#888888') for c in merged['category']]

fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bars = ax.barh(range(len(merged)), merged['vol_oi_ratio'].values, height=0.55,
               color=bar_colors, alpha=0.9, edgecolor='#1a1a1a', linewidth=0.5)

# Labels
labels = []
for _, row in merged.iterrows():
    oi_m = row['open_interest_usd'] / 1e6
    labels.append(f"{row['subsubcategory']} (${oi_m:.0f}M OI)")

ax.set_yticks(range(len(merged)))
ax.set_yticklabels(labels, fontsize=11, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# Value labels
for i, (val, color) in enumerate(zip(merged['vol_oi_ratio'].values, bar_colors)):
    ax.text(val + 0.05, i, f'{val:.1f}x', va='center', ha='left',
            fontsize=11, fontweight='bold', color=color)

# X-axis
x_max = merged['vol_oi_ratio'].max()
x_ticks = [0, 2, 4, 6, 8]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{v}x' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, x_max + 1.5)

# Reference line at 1.0x
ax.axvline(x=1.0, color=COLORS['text_secondary'], alpha=0.5,
           linestyle='--', linewidth=1, zorder=1)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_activity_ratio.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_activity_ratio.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("\nChart 3 saved: Volume/OI Activity Ratio")
print("\nTop activity markets:")
for _, row in merged.sort_values('vol_oi_ratio', ascending=False).iterrows():
    print(f"  {row['subsubcategory']}: {row['vol_oi_ratio']:.2f}x "
          f"(Vol ${row['volume_usd']/1e6:.1f}M, OI ${row['open_interest_usd']/1e6:.1f}M)")
