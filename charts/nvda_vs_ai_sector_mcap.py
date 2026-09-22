import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG, area_glow

# =============================================================================
# Data
# =============================================================================
df_mcap = pd.read_csv('data/ai_crypto_sector_market_cap.csv', parse_dates=['Date'])
df_idx = pd.read_csv('data/nvda_ai_tokens_indexed_performance.csv', parse_dates=['Date'])

output_dir = 'outputs/charts/nvidia/correlation'
Path(output_dir).mkdir(parents=True, exist_ok=True)

NVDA_C = '#76B900'
MCAP_C = '#fac858'

# =============================================================================
# Chart: Dual Y-axis - NVDA indexed vs AI sector market cap
# =============================================================================
setup_font()
fig, ax1 = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')

dates = df_mcap['Date']
ai_mcap = df_mcap['AI_Sector_Mcap_Billion'].values

# Left axis: AI sector market cap (area)
ax1.fill_between(dates, 0, ai_mcap, color=MCAP_C, alpha=0.15, linewidth=0, zorder=2)
ax1.plot(dates, ai_mcap, color=MCAP_C, linewidth=2.0, zorder=4)
ax1.scatter(dates.iloc[-1], ai_mcap[-1], color=MCAP_C, s=50, zorder=5, edgecolors='none')
ax1.annotate(f'${ai_mcap[-1]:.0f}B', (dates.iloc[-1], ai_mcap[-1]),
             textcoords="offset points", xytext=(8, -10),
             fontsize=12, fontweight='bold', color=MCAP_C, zorder=6)

# Right axis: NVDA indexed
ax2 = ax1.twinx()
nvda_idx = df_idx['NVDA_Indexed'].values
nvda_dates = df_idx['Date']

# NVDA area glow
n_layers = 40
for i in range(n_layers):
    frac = i / n_layers
    alpha = 0.12 * (frac ** 2.5)
    lower = nvda_idx * frac
    upper = nvda_idx * (frac + 1 / n_layers)
    ax2.fill_between(nvda_dates, lower, upper,
                     color=NVDA_C, alpha=alpha, linewidth=0, zorder=1)

ax2.plot(nvda_dates, nvda_idx, color=NVDA_C, linewidth=2.2, zorder=3)
ax2.scatter(nvda_dates.iloc[-1], nvda_idx[-1], color=NVDA_C, s=50, zorder=5,
            edgecolors='none')
ax2.annotate(f'{nvda_idx[-1]:.0f}', (nvda_dates.iloc[-1], nvda_idx[-1]),
             textcoords="offset points", xytext=(8, 5),
             fontsize=12, fontweight='bold', color=NVDA_C, zorder=6)

# Divergence annotation
import datetime
ax1.annotate('', xy=(datetime.datetime(2025, 9, 1), 14),
             xytext=(datetime.datetime(2025, 3, 1), 14),
             arrowprops=dict(arrowstyle='->', color='#ef5350', alpha=0.4, lw=1.5))
ax1.text(datetime.datetime(2025, 6, 1), 15.5, 'Divergence',
         ha='center', fontsize=10, fontweight='bold', color='#ef5350', alpha=0.5)

# GTC markers
for gtc_date, label in [(datetime.datetime(2024, 3, 18), 'GTC 24'),
                          (datetime.datetime(2025, 3, 17), 'GTC 25'),
                          (datetime.datetime(2026, 3, 16), 'GTC 26')]:
    ax1.axvline(x=gtc_date, color='#ffffff', linewidth=0.8, alpha=0.15,
                linestyle=':', zorder=1)
    ax1.text(gtc_date, 28, label, ha='center', fontsize=8, fontweight='bold',
             color=COLORS['text_secondary'], alpha=0.5)

# --- Left Y-axis (AI sector mcap) ---
n_ticks = 5
y1_ticks = [0, 8, 16, 24, 32]
ax1.set_yticks(y1_ticks)
ax1.set_yticklabels([f'${v}B' for v in y1_ticks],
                     fontsize=13, fontweight='bold',
                     color=MCAP_C)
ax1.set_ylim(0, 33)
ax1.tick_params(axis='y', length=0, pad=15)

# --- Right Y-axis (NVDA indexed, aligned ticks) ---
y2_ticks = np.linspace(0, 400, n_ticks)
ax2.set_yticks(y2_ticks)
ax2.set_yticklabels([f'{int(v)}' for v in y2_ticks],
                     fontsize=13, fontweight='bold',
                     color=NVDA_C)
ax2.set_ylim(0, 412)
ax2.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
plt.setp(ax1.xaxis.get_majorticklabels(), fontsize=11, fontweight='bold',
         color=COLORS['text_secondary'], rotation=45, ha='right')
ax1.tick_params(axis='x', length=0, pad=8)

# --- Grid (left axis only) ---
ax1.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax1.set_axisbelow(True)

# --- Spines ---
for spine in ax1.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

# Series labels
ax1.text(0.02, 0.95, 'AI Crypto Sector Mcap', transform=ax1.transAxes,
         fontsize=12, fontweight='bold', color=MCAP_C, ha='left', va='top')
ax1.text(0.02, 0.87, 'NVDA (indexed=100)', transform=ax1.transAxes,
         fontsize=12, fontweight='bold', color=NVDA_C, ha='left', va='top')

# --- Save ---
fig.savefig(f'{output_dir}/nvda_vs_ai_sector_mcap.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/nvda_vs_ai_sector_mcap.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/nvda_vs_ai_sector_mcap.png")
