import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/ai_datacenter_power.csv')

output_dir = 'outputs/charts/nvidia/power'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Colors
AI_C = '#76B900'
NON_AI_C = '#5470c6'

# =============================================================================
# Chart: Stacked Area - AI vs Non-AI Power Consumption
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

years = df['Year'].values
ai_power = df['AI_Power_TWh'].values
non_ai_power = df['Non_AI_Power_TWh'].values
total_power = df['Global_DC_Power_TWh'].values

# Stacked area
ax.fill_between(years, 0, non_ai_power, color=NON_AI_C, alpha=0.25, linewidth=0, zorder=2)
ax.fill_between(years, non_ai_power, total_power, color=AI_C, alpha=0.35, linewidth=0, zorder=2)

# Lines on top
ax.plot(years, total_power, color=COLORS['text'], linewidth=2.0, zorder=4, alpha=0.8)
ax.plot(years, non_ai_power, color=NON_AI_C, linewidth=1.5, zorder=3, alpha=0.6,
        linestyle='--')

# AI power line (boundary between areas)
ax.plot(years, ai_power, color=AI_C, linewidth=0, zorder=3)

# Endpoint dots
ax.scatter(years[-1], total_power[-1], color=COLORS['text'], s=50, zorder=5, edgecolors='none')
ax.scatter(years[-1], ai_power[-1], color=AI_C, s=50, zorder=5, edgecolors='none')

# Labels at end
ax.annotate(f'{total_power[-1]:,.0f} TWh', (years[-1], total_power[-1]),
            textcoords="offset points", xytext=(8, 5),
            fontsize=12, fontweight='bold', color=COLORS['text'], zorder=6)

# AI share annotation at 2026 (current year)
idx_2026 = np.where(years == 2026)[0][0]
ai_mid = non_ai_power[idx_2026] + ai_power[idx_2026] / 2
ax.annotate(f'AI: {df["AI_Share_Pct"].values[idx_2026]}%',
            (2026, non_ai_power[idx_2026] + ai_power[idx_2026] * 0.5),
            textcoords="offset points", xytext=(0, 0),
            fontsize=11, fontweight='bold', color=AI_C, ha='center', zorder=6)

# AI share at 2030
idx_2030 = np.where(years == 2030)[0][0]
ax.annotate(f'AI: {df["AI_Share_Pct"].values[idx_2030]}%',
            (2030, non_ai_power[idx_2030] + ai_power[idx_2030] * 0.5),
            textcoords="offset points", xytext=(0, 0),
            fontsize=11, fontweight='bold', color=AI_C, ha='center', zorder=6)

# Vertical dashed line at 2026 (current)
ax.axvline(x=2026, color=COLORS['text_secondary'], linewidth=1.0, alpha=0.3,
           linestyle=':', zorder=1)
ax.text(2026, 1850, 'NOW', ha='center', fontsize=10, fontweight='bold',
        color=COLORS['text_secondary'], alpha=0.6)

# --- Y-axis ---
y_ticks = [0, 500, 1000, 1500, 2000]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v:,} TWh' for v in y_ticks],
                    fontsize=13, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 1950)
ax.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years],
                    fontsize=12, fontweight='bold',
                    color=COLORS['text_secondary'], rotation=45, ha='right')
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(2020, 2030)

# --- Grid ---
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# --- Spines ---
for spine in ax.spines.values():
    spine.set_visible(False)

# --- Save ---
fig.savefig(f'{output_dir}/ai_datacenter_power.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/ai_datacenter_power.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/ai_datacenter_power.png")
