import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import datetime

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('data/nvda_ai_tokens_indexed_performance.csv', parse_dates=['Date'])

output_dir = 'outputs/charts/nvidia/correlation'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Colors
NVDA_C = '#76B900'
RENDER_C = '#ee6666'
TAO_C = '#5470c6'
FET_C = '#fac858'
NEAR_C = '#73c0de'

# =============================================================================
# Chart: Indexed Performance (base 100)
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

dates = df['Date']

# NVIDIA (thick, prominent)
ax.plot(dates, df['NVDA_Indexed'], color=NVDA_C, linewidth=2.5, zorder=5)

# AI Tokens (thinner)
ax.plot(dates, df['RENDER_Indexed'], color=RENDER_C, linewidth=1.5, zorder=4, alpha=0.85)
ax.plot(dates, df['TAO_Indexed'], color=TAO_C, linewidth=1.5, zorder=4, alpha=0.85)
ax.plot(dates, df['FET_Indexed'], color=FET_C, linewidth=1.5, zorder=4, alpha=0.85)
ax.plot(dates, df['NEAR_Indexed'], color=NEAR_C, linewidth=1.5, zorder=4, alpha=0.85)

# Endpoint dots + labels
tokens = [
    ('NVDA_Indexed', NVDA_C, 'NVDA', 8),
    ('RENDER_Indexed', RENDER_C, 'RENDER', -12),
    ('TAO_Indexed', TAO_C, 'TAO', 8),
    ('FET_Indexed', FET_C, 'FET', -12),
    ('NEAR_Indexed', NEAR_C, 'NEAR', -5),
]
for col, color, label, offset_y in tokens:
    last_val = df[col].iloc[-1]
    ax.scatter(dates.iloc[-1], last_val, color=color, s=40, zorder=6, edgecolors='none')
    pct = last_val - 100
    sign = '+' if pct >= 0 else ''
    ax.annotate(f'{label} {sign}{pct:.0f}%', (dates.iloc[-1], last_val),
                textcoords="offset points", xytext=(8, offset_y),
                fontsize=10, fontweight='bold', color=color, zorder=7)

# 100 baseline
ax.axhline(y=100, color=COLORS['text_secondary'], linewidth=1.0, alpha=0.4,
           linestyle='-', zorder=1)

# GTC event markers
gtc_dates = [
    (datetime.datetime(2024, 3, 18), 'GTC 24'),
    (datetime.datetime(2025, 3, 17), 'GTC 25'),
    (datetime.datetime(2026, 3, 16), 'GTC 26'),
]
for gtc_date, label in gtc_dates:
    ax.axvline(x=gtc_date, color='#ffffff', linewidth=0.8, alpha=0.2,
               linestyle=':', zorder=1)
    ax.text(gtc_date, ax.get_ylim()[1] * 0.95, label, ha='center', fontsize=8,
            fontweight='bold', color=COLORS['text_secondary'], alpha=0.6)

# Phase annotations
ax.annotate('Coupled', xy=(datetime.datetime(2024, 3, 1), 400),
            fontsize=11, fontweight='bold', color='#26a69a', alpha=0.5,
            ha='center')
ax.annotate('Decoupled', xy=(datetime.datetime(2025, 6, 1), 280),
            fontsize=11, fontweight='bold', color='#ef5350', alpha=0.5,
            ha='center')

# --- Y-axis ---
y_ticks = [0, 100, 200, 300, 400, 500]
ax.set_yticks(y_ticks)
ax.set_yticklabels([str(v) for v in y_ticks],
                    fontsize=13, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(-10, 560)
ax.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
plt.setp(ax.xaxis.get_majorticklabels(), fontsize=11, fontweight='bold',
         color=COLORS['text_secondary'], rotation=45, ha='right')
ax.tick_params(axis='x', length=0, pad=8)

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
fig.savefig(f'{output_dir}/nvda_vs_ai_tokens_indexed.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/nvda_vs_ai_tokens_indexed.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/nvda_vs_ai_tokens_indexed.png")
