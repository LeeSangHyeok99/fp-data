import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/crypto-payments/volume'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/crypto_payment_card_monthly_volume.csv')
df['date'] = pd.to_datetime(df['date'])

# Filter from Jan 2024 onwards (earlier months have negligible data)
df = df[df['date'] >= '2024-01-01'].reset_index(drop=True)

# Convert to millions
all_cards = ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Cypher', 'Gnosis', 'Ready', 'Other']
for c in all_cards:
    df[c] = df[c] / 1e6

# Merge non-top-5 into Others
top5 = ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria']
others = [c for c in all_cards if c not in top5]
df['Others'] = sum(df[c] for c in others)
cards = top5 + ['Others']

# Brand colors
CARD_COLORS = {
    'RedotPay': '#E41B38',   # official brand red
    'EtherFi': '#655EA8',    # ether.fi purple
    'KAST': '#C9C7C5',       # KAST site neutral tone
    'Karta': '#CCFF00',      # lime green
    'Tria': '#5E33F7',       # tria purple
    'Others': '#555555',
}

# Order: largest on bottom
stack_order = ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Others']

# =============================================================================
# Chart: Stacked Bar — Monthly Crypto Card Volumes
# =============================================================================
setup_font()

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bar_width = 0.75

bottom = np.zeros(len(df))
for card in stack_order:
    vals = df[card].values
    ax.bar(x, vals, bottom=bottom, width=bar_width,
           color=CARD_COLORS[card], alpha=0.9, zorder=3, label=card)
    bottom += vals

# Y axis — clean ticks in $M
y_ticks = [0, 200, 400, 600]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${int(v)}M' for v in y_ticks],
                    fontsize=15, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 700)
ax.tick_params(axis='y', length=0, pad=10)

# X axis — show every 3 months, aligned from end
tick_positions = list(range(len(df) - 1, -1, -3))
tick_positions.reverse()
tick_labels = [df.iloc[i]['date'].strftime('%b %Y') for i in tick_positions]
ax.set_xticks([x[i] for i in tick_positions])
ax.set_xticklabels(tick_labels, fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'],
                    rotation=45, ha='right')
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])
ax.set_xlim(-0.6, len(df) - 0.4)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/crypto_payment_card_volume.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()

# =============================================================================
# Stats
# =============================================================================
latest = df.iloc[-1]
total_latest = sum(latest[c] for c in ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Others'])
redot_share = latest['RedotPay'] / total_latest * 100

# Monthly totals
df['total'] = sum(df[c] for c in ['RedotPay', 'EtherFi', 'KAST', 'Karta', 'Tria', 'Others'])

print(f'Done: crypto_payment_card_volume.png / .svg')
print(f'Mar 2026 total: ${total_latest:.1f}M')
print(f'RedotPay share: {redot_share:.1f}%')
print(f'RedotPay Mar 2026: ${latest["RedotPay"]:.1f}M')
print(f'EtherFi Mar 2026: ${latest["EtherFi"]:.1f}M')
print(f'KAST Mar 2026: ${latest["KAST"]:.1f}M')
print(f'Karta Mar 2026: ${latest["Karta"]:.1f}M')
print(f'Tria Mar 2026: ${latest["Tria"]:.1f}M')

# Growth
mar26 = df[df['date'] == '2026-03-01']['total'].values[0]
mar25 = df[df['date'] == '2025-03-01']['total'].values[0]
print(f'YoY growth: ${mar25:.1f}M → ${mar26:.1f}M ({(mar26/mar25 - 1)*100:.0f}%)')
