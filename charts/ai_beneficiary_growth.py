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
df = pd.read_csv('outputs/data/ai_beneficiary_growth.csv')
df = df.sort_values('Growth_Pct', ascending=True)

output_dir = 'outputs/charts/nvidia/gtc2026'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Chart: Paired horizontal bars (2024 vs 2026 revenue)
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 7), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = np.arange(len(df))
bar_height = 0.35

# 2024 bars (lighter)
bars_2024 = ax.barh(y + bar_height/2, df['Revenue_2024_B'].values, height=bar_height,
                     zorder=3, edgecolor='none', alpha=0.4)
# 2026 bars (solid)
bars_2026 = ax.barh(y - bar_height/2, df['Revenue_2026_B'].values, height=bar_height,
                     zorder=3, edgecolor='none', alpha=0.85)

# Apply colors
for b24, b26, color in zip(bars_2024, bars_2026, df['Color'].values):
    b24.set_color(color)
    b26.set_color(color)

# Growth % labels
for i, (rev24, rev26, growth) in enumerate(zip(df['Revenue_2024_B'].values,
                                                df['Revenue_2026_B'].values,
                                                df['Growth_Pct'].values)):
    ax.text(rev26 + 0.2, i - bar_height/2, f'${rev26:.1f}B (+{growth:.0f}%)',
            va='center', ha='left', fontsize=11, fontweight='bold',
            color='#26a69a', zorder=6)
    ax.text(rev24 + 0.2, i + bar_height/2, f'${rev24:.1f}B',
            va='center', ha='left', fontsize=10, fontweight='bold',
            color=COLORS['text_secondary'], alpha=0.6, zorder=6)

# Y-axis
labels = [f"{row['Company']}" for _, row in df.iterrows()]
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
x_ticks = [0, 5, 10, 15]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}B' for v in x_ticks],
                    fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.set_xlim(0, 17)
ax.tick_params(axis='x', length=0, pad=8)

# Year labels in top-right area
ax.text(0.92, 0.95, '2026E', transform=ax.transAxes, fontsize=14, fontweight='bold',
        color=COLORS['text'], ha='right', va='top')
ax.text(0.92, 0.88, '2024', transform=ax.transAxes, fontsize=14, fontweight='bold',
        color=COLORS['text_secondary'], alpha=0.5, ha='right', va='top')

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Save
fig.savefig(f'{output_dir}/ai_beneficiary_growth.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/ai_beneficiary_growth.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/ai_beneficiary_growth.png")
