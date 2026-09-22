import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/prediction_market_oi.csv')

output_dir = 'outputs/charts/prediction_markets'
Path(output_dir).mkdir(parents=True, exist_ok=True)

KALSHI_C = '#5470c6'
POLY_C = '#91cc75'

# Category-level aggregation
pivot = df.groupby(['category', 'source'])['open_interest_usd'].sum().unstack(fill_value=0)
pivot = pivot / 1e6

# Ensure both columns exist
for col in ['Kalshi', 'Polymarket']:
    if col not in pivot.columns:
        pivot[col] = 0

pivot['total'] = pivot['Kalshi'] + pivot['Polymarket']
pivot = pivot.sort_values('total', ascending=False)

# Calculate shares
pivot['kalshi_share'] = pivot['Kalshi'] / pivot['total'] * 100
pivot['poly_share'] = pivot['Polymarket'] / pivot['total'] * 100

# =============================================================================
# Chart: Diverging bar (Kalshi left, Polymarket right)
# =============================================================================
setup_font()

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

categories = pivot.index.tolist()
y = np.arange(len(categories))
bar_h = 0.52

# Kalshi goes left (negative), Polymarket goes right (positive)
kalshi_vals = pivot['Kalshi'].values
poly_vals = pivot['Polymarket'].values

# Draw bars
bars_k = ax.barh(y, -kalshi_vals, height=bar_h, color=KALSHI_C, alpha=0.9,
                 edgecolor='#1a1a1a', linewidth=0.5)
bars_p = ax.barh(y, poly_vals, height=bar_h, color=POLY_C, alpha=0.9,
                 edgecolor='#1a1a1a', linewidth=0.5)

# Value labels
for i in range(len(categories)):
    # Kalshi label (left side)
    if kalshi_vals[i] > 2:
        ax.text(-kalshi_vals[i] - 2, y[i], f'${kalshi_vals[i]:.0f}M',
                va='center', ha='right', fontsize=10, fontweight='bold', color=KALSHI_C)
    # Polymarket label (right side)
    if poly_vals[i] > 2:
        ax.text(poly_vals[i] + 2, y[i], f'${poly_vals[i]:.0f}M',
                va='center', ha='left', fontsize=10, fontweight='bold', color=POLY_C)

# Y-axis: category labels on the left side
ax.set_yticks(y)
ax.set_yticklabels(categories, fontsize=13, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
max_val = max(kalshi_vals.max(), poly_vals.max())
x_step = 50
x_ticks = np.arange(-200, 201, x_step)
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${abs(v):.0f}M' for v in x_ticks],
                   fontsize=11, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(-210, 160)

# Center line
ax.axvline(x=0, color=COLORS['text_secondary'], alpha=0.4, linewidth=0.8, zorder=1)

# Platform labels at top
ax.text(-105, len(categories) - 0.3, 'Kalshi', ha='center', va='bottom',
        fontsize=15, fontweight='bold', color=KALSHI_C)
ax.text(70, len(categories) - 0.3, 'Polymarket', ha='center', va='bottom',
        fontsize=15, fontweight='bold', color=POLY_C)

total_kalshi = kalshi_vals.sum()
total_poly = poly_vals.sum()
ax.text(-105, len(categories) + 0.05, f'${total_kalshi:.0f}M total',
        ha='center', va='bottom', fontsize=10, fontweight='bold', color=KALSHI_C, alpha=0.6)
ax.text(70, len(categories) + 0.05, f'${total_poly:.0f}M total',
        ha='center', va='bottom', fontsize=10, fontweight='bold', color=POLY_C, alpha=0.6)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_diverging.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_diverging.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print("Chart saved: Kalshi vs Polymarket Diverging Bar")
print(f"\nKalshi Total: ${total_kalshi:.0f}M")
print(f"Polymarket Total: ${total_poly:.0f}M")
print(f"\nCategory breakdown:")
for cat in pivot.index:
    k = pivot.loc[cat, 'Kalshi']
    p = pivot.loc[cat, 'Polymarket']
    ks = pivot.loc[cat, 'kalshi_share']
    ps = pivot.loc[cat, 'poly_share']
    print(f"  {cat}: Kalshi ${k:.0f}M ({ks:.0f}%) | Polymarket ${p:.0f}M ({ps:.0f}%)")
