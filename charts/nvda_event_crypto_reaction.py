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
# Data - manually curated key events
# =============================================================================
events = [
    ('Q4 FY24\nEarnings', 'Feb 24', 9.0, 6.0),
    ('GTC 2024\nKeynote', 'Mar 24', 2.5, 16.8),
    ('Q1 FY25\nEarnings', 'May 24', 9.3, -5.0),
    ('Q2 FY25\nEarnings', 'Aug 24', -6.4, -6.0),
    ('Q3 FY25\nEarnings', 'Nov 24', 0.5, 5.0),
    ('Q4 FY25\nEarnings', 'Feb 25', 3.0, 10.0),
    ('GTC 2025\nKeynote', 'Mar 25', -3.4, -6.0),
    ('Q1 FY26\nEarnings', 'May 25', 4.0, -3.0),
    ('Q2 FY26\nEarnings', 'Aug 25', 2.0, 5.0),
    ('Q3 FY26\nEarnings', 'Nov 25', -5.0, -8.0),
    ('GTC 2026\nKeynote', 'Mar 26', 2.0, 12.0),
]

labels = [e[0] for e in events]
dates = [e[1] for e in events]
nvda_moves = [e[2] for e in events]
crypto_moves = [e[3] for e in events]

output_dir = 'outputs/charts/nvidia/correlation'
Path(output_dir).mkdir(parents=True, exist_ok=True)

NVDA_C = '#76B900'
CRYPTO_C = '#fac858'

# =============================================================================
# Chart: Grouped Bar - NVDA vs AI Crypto reaction per event
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(16, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(events))
bar_width = 0.35

# Bars
bars_nvda = ax.bar(x - bar_width/2, nvda_moves, bar_width, color=NVDA_C,
                    alpha=0.85, zorder=3, edgecolor='none')
bars_crypto = ax.bar(x + bar_width/2, crypto_moves, bar_width, color=CRYPTO_C,
                      alpha=0.85, zorder=3, edgecolor='none')

# Color negative bars differently
for bar, val in zip(bars_nvda, nvda_moves):
    if val < 0:
        bar.set_alpha(0.5)
for bar, val in zip(bars_crypto, crypto_moves):
    if val < 0:
        bar.set_alpha(0.5)

# Value labels on bars
for i, (nv, cr) in enumerate(zip(nvda_moves, crypto_moves)):
    offset_nv = 0.3 if nv >= 0 else -0.8
    offset_cr = 0.3 if cr >= 0 else -0.8
    sign_nv = '+' if nv > 0 else ''
    sign_cr = '+' if cr > 0 else ''
    ax.text(i - bar_width/2, nv + offset_nv, f'{sign_nv}{nv:.1f}%',
            ha='center', va='bottom' if nv >= 0 else 'top',
            fontsize=8, fontweight='bold', color=NVDA_C, zorder=6)
    ax.text(i + bar_width/2, cr + offset_cr, f'{sign_cr}{cr:.1f}%',
            ha='center', va='bottom' if cr >= 0 else 'top',
            fontsize=8, fontweight='bold', color=CRYPTO_C, zorder=6)

# Zero line
ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=1.0, alpha=0.5, zorder=2)

# Highlight GTC events
for i, label in enumerate(labels):
    if 'GTC' in label:
        ax.axvspan(i - 0.5, i + 0.5, color='#ffffff', alpha=0.03, zorder=0)

# --- X-axis ---
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9, fontweight='bold',
                    color=COLORS['text_secondary'], ha='center')
ax.tick_params(axis='x', length=0, pad=8)

# --- Y-axis ---
y_ticks = [-10, -5, 0, 5, 10, 15, 20]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks],
                    fontsize=12, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(-12, 22)
ax.tick_params(axis='y', length=0, pad=15)

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

# Series indicator
ax.text(0.02, 0.95, 'NVDA', transform=ax.transAxes, fontsize=13, fontweight='bold',
        color=NVDA_C, ha='left', va='top')
ax.text(0.08, 0.95, 'AI Crypto', transform=ax.transAxes, fontsize=13, fontweight='bold',
        color=CRYPTO_C, ha='left', va='top')

# --- Save ---
fig.savefig(f'{output_dir}/nvda_event_crypto_reaction.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/nvda_event_crypto_reaction.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/nvda_event_crypto_reaction.png")
