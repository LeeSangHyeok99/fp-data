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
df = pd.read_csv('outputs/data/prediction_market_themes.csv')

output_dir = 'outputs/charts/prediction_markets'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Theme-level aggregation
theme_oi = df.groupby('theme')['open_interest_usd'].sum().sort_values(ascending=True)
theme_vol = df.groupby('theme')['volume_usd'].sum()
theme_oi_m = theme_oi / 1e6

# Theme colors
theme_colors = {
    'Science & Tech': '#9a60b4',
    'Pop Culture':    '#ea7ccc',
    'Crypto':         '#f7931a',
    'Macro & Rates':  '#73c0de',
    'Geopolitics':    '#ef5350',
    'US Elections':   '#5470c6',
    'Sports Betting': '#91cc75',
}

colors = [theme_colors.get(t, '#888888') for t in theme_oi.index]

# =============================================================================
# Chart: Theme OI with CFTC status markers
# =============================================================================
setup_font()

fig, ax = plt.subplots(figsize=(10.67, 5.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = np.arange(len(theme_oi_m))

bars = ax.barh(y, theme_oi_m.values, height=0.55,
               color=colors, alpha=0.9, edgecolor='#1a1a1a', linewidth=0.5)

# Value labels + percentage
total_oi = theme_oi.sum()
for i, (val, color, theme) in enumerate(zip(theme_oi_m.values, colors, theme_oi.index)):
    pct = theme_oi[theme] / total_oi * 100
    ax.text(val + 2, i, f'${val:.0f}M ({pct:.0f}%)',
            va='center', ha='left', fontsize=10, fontweight='bold', color=color)

# Y-axis
ax.set_yticks(y)
ax.set_yticklabels(theme_oi.index, fontsize=13, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
x_ticks = [0, 50, 100, 150, 200]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}M' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, 240)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_themes.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_themes.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print("Chart 1 saved: Theme OI Distribution")
for theme in theme_oi.sort_values(ascending=False).index:
    pct = theme_oi[theme] / total_oi * 100
    vol = theme_vol[theme] / 1e6
    ratio = theme_vol[theme] / theme_oi[theme]
    print(f"  {theme}: OI ${theme_oi[theme]/1e6:.0f}M ({pct:.1f}%), Vol ${vol:.0f}M, V/OI {ratio:.2f}x")

# =============================================================================
# Chart 2: Theme OI - Kalshi vs Polymarket split (stacked horizontal bar)
# =============================================================================
setup_font()

KALSHI_C = '#5470c6'
POLY_C = '#91cc75'

theme_platform = df.groupby(['theme', 'source'])['open_interest_usd'].sum().unstack(fill_value=0) / 1e6
for col in ['Kalshi', 'Polymarket']:
    if col not in theme_platform.columns:
        theme_platform[col] = 0
theme_platform['total'] = theme_platform.sum(axis=1)
theme_platform = theme_platform.sort_values('total', ascending=True)

fig, ax = plt.subplots(figsize=(10.67, 5.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = np.arange(len(theme_platform))
kalshi_vals = theme_platform['Kalshi'].values
poly_vals = theme_platform['Polymarket'].values
totals = kalshi_vals + poly_vals

# Normalized stacked bars (100% width, actual width = total OI)
bar_h = 0.55
for i in range(len(theme_platform)):
    total = totals[i]
    if total == 0:
        continue
    k_w = total * (kalshi_vals[i] / total)
    p_w = total * (poly_vals[i] / total)

    # Draw bars
    ax.barh(y[i], k_w, height=bar_h, color=KALSHI_C, alpha=0.9,
            edgecolor='#1a1a1a', linewidth=0.5)
    ax.barh(y[i], p_w, height=bar_h, left=k_w, color=POLY_C, alpha=0.9,
            edgecolor='#1a1a1a', linewidth=0.5)

    # Percentage labels inside (only if segment wide enough)
    k_pct = kalshi_vals[i] / total * 100
    p_pct = poly_vals[i] / total * 100

    if k_w > 18:
        ax.text(k_w / 2, y[i], f'{k_pct:.0f}%',
                va='center', ha='center', fontsize=10, fontweight='bold', color='white')
    if p_w > 18:
        ax.text(k_w + p_w / 2, y[i], f'{p_pct:.0f}%',
                va='center', ha='center', fontsize=10, fontweight='bold', color='#1a1a1a')

    # Total OI label (white/light color)
    ax.text(total + 2, y[i], f'${total:.0f}M',
            va='center', ha='left', fontsize=10, fontweight='bold',
            color=COLORS['text_secondary'])

# Y-axis
ax.set_yticks(y)
ax.set_yticklabels(theme_platform.index, fontsize=13, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
x_ticks = [0, 50, 100, 150, 200]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}M' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, 240)

# No legend (per style rules)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_themes_platform.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_themes_platform.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print("\nChart 2 saved: Theme OI by Platform (Stacked)")
print(f"\nTotal OI: ${total_oi/1e6:.0f}M")
