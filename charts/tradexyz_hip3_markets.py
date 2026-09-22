import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/tradexyz'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/hip3_markets_20260406.csv')

# Category colors
CAT_COLORS = {
    'Commodities': '#C9A84C',  # Gold
    'Indices': '#5470c6',      # Blue
    'Equities': '#91cc75',     # Green
    'Crypto': '#ee6666',       # Red
}

# =============================================================================
# Chart 1: Top 12 Markets by OI (Horizontal Bar)
# =============================================================================
setup_font()

top = df.nlargest(12, 'oi_m').sort_values('oi_m')  # ascending for horizontal bar

fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bars = ax.barh(
    range(len(top)),
    top['oi_m'],
    height=0.65,
    color=[CAT_COLORS[c] for c in top['category']],
    alpha=0.85,
    zorder=3,
)

# Labels: ticker + deployer
for i, (_, row) in enumerate(top.iterrows()):
    # Ticker label on bar
    label_x = row['oi_m'] + 8
    ax.text(label_x, i, f"${row['oi_m']:.0f}M",
            va='center', ha='left',
            fontsize=14, fontweight='bold',
            color=COLORS['text'])

# Y axis: market names
ax.set_yticks(range(len(top)))
labels = []
for _, row in top.iterrows():
    deployer_tag = f" ({row['deployer']})" if row['deployer'] != 'TradeXYZ' else ''
    labels.append(f"{row['ticker']}{deployer_tag}")
ax.set_yticklabels(labels,
                    fontsize=16, fontweight='bold',
                    color=COLORS['text'])

# X axis
x_max = top['oi_m'].max()
x_ceil = np.ceil(x_max / 100) * 100 + 100
x_ticks = np.arange(0, x_ceil + 1, 100)
if len(x_ticks) > 7:
    x_ticks = np.arange(0, x_ceil + 1, 200)
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${int(v)}M' for v in x_ticks],
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_xlim(0, x_ceil)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', length=0, pad=10)
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hip3_top_markets_oi.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Chart 2: OI by Category (Donut)
# =============================================================================
cat_data = df.groupby('category').agg(oi=('oi_m', 'sum')).sort_values('oi', ascending=False)
cat_data['share'] = cat_data['oi'] / cat_data['oi'].sum() * 100

fig2, ax2 = plt.subplots(figsize=(6, 6), dpi=DPI)
fig2.patch.set_alpha(0)
ax2.set_facecolor('none')

colors = [CAT_COLORS[c] for c in cat_data.index]
wedges, texts = ax2.pie(
    cat_data['oi'],
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.4, edgecolor='none'),
    pctdistance=0.75,
)

# Category labels outside
for i, (cat, row) in enumerate(cat_data.iterrows()):
    ang = (wedges[i].theta2 + wedges[i].theta1) / 2
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))

    ha = 'left' if x > 0 else 'right'
    ax2.annotate(
        f'{cat}\n{row["share"]:.0f}%',
        xy=(0.7 * x, 0.7 * y),
        xytext=(1.25 * x, 1.15 * y),
        ha=ha, va='center',
        fontsize=14, fontweight='bold',
        color=COLORS['text'],
        arrowprops=dict(arrowstyle='-', color=COLORS['text_secondary'], lw=1),
    )

# Center text
ax2.text(0, 0.05, f'${cat_data["oi"].sum()/1e3:.1f}B', ha='center', va='center',
         fontsize=28, fontweight='bold', color=COLORS['text'])
ax2.text(0, -0.12, 'OI', ha='center', va='center',
         fontsize=16, fontweight='bold', color=COLORS['text_secondary'])

fig2.tight_layout()

for fmt in ['png', 'svg']:
    fig2.savefig(
        f'{output_dir}/hip3_oi_by_category.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Chart 3: Deployer Share (Donut)
# =============================================================================
dep_data = df.groupby('deployer').agg(oi=('oi_m', 'sum')).sort_values('oi', ascending=False)
dep_data['share'] = dep_data['oi'] / dep_data['oi'].sum() * 100

DEP_COLORS = {
    'TradeXYZ': '#f97316',
    'Dreamcash': '#73c0de',
    'Hyena': '#9a60b4',
    'Felix': '#91cc75',
    'Markets': '#fac858',
    'Ventuals': '#ee6666',
}

fig3, ax3 = plt.subplots(figsize=(6, 6), dpi=DPI)
fig3.patch.set_alpha(0)
ax3.set_facecolor('none')

colors3 = [DEP_COLORS.get(d, '#787b86') for d in dep_data.index]
wedges3, _ = ax3.pie(
    dep_data['oi'],
    colors=colors3,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.4, edgecolor='none'),
)

for i, (dep, row) in enumerate(dep_data.iterrows()):
    ang = (wedges3[i].theta2 + wedges3[i].theta1) / 2
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    ha = 'left' if x > 0 else 'right'

    label = f'{dep}\n{row["share"]:.1f}%'
    if row['share'] < 2:
        continue  # skip tiny slices

    ax3.annotate(
        label,
        xy=(0.7 * x, 0.7 * y),
        xytext=(1.25 * x, 1.15 * y),
        ha=ha, va='center',
        fontsize=14, fontweight='bold',
        color=COLORS['text'],
        arrowprops=dict(arrowstyle='-', color=COLORS['text_secondary'], lw=1),
    )

ax3.text(0, 0.05, f'${dep_data["oi"].sum()/1e3:.1f}B', ha='center', va='center',
         fontsize=28, fontweight='bold', color=COLORS['text'])
ax3.text(0, -0.12, 'OI', ha='center', va='center',
         fontsize=16, fontweight='bold', color=COLORS['text_secondary'])

fig3.tight_layout()

for fmt in ['png', 'svg']:
    fig3.savefig(
        f'{output_dir}/hip3_oi_by_deployer.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print('Done: hip3_top_markets_oi, hip3_oi_by_category, hip3_oi_by_deployer')
print(f'\nCategory breakdown:')
for cat, row in cat_data.iterrows():
    print(f'  {cat}: ${row["oi"]:.0f}M ({row["share"]:.1f}%)')
print(f'\nDeployer breakdown:')
for dep, row in dep_data.iterrows():
    print(f'  {dep}: ${row["oi"]:.0f}M ({row["share"]:.1f}%)')
