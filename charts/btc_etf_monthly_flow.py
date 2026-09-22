import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG, POSITIVE_COLOR, NEGATIVE_COLOR

output_dir = 'outputs/charts/bitcoin/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/btc_etf_monthly_flow.csv')
df['month_dt'] = pd.to_datetime(df['month'] + '-01')
df['label'] = df['month_dt'].dt.strftime('%b %Y')

# =============================================================================
# Chart: Monthly Net Flow Bar Chart — HRC theme
# =============================================================================
setup_font()

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bar_width = 0.7

colors = [POSITIVE_COLOR if v >= 0 else NEGATIVE_COLOR for v in df['net_flow_b']]

bars = ax.bar(x, df['net_flow_b'], width=bar_width, color=colors, alpha=0.85, zorder=3)

# Highlight March 2026 (last bar) with annotation
last_val = df['net_flow_b'].iloc[-1]
ax.annotate(f'+${last_val:.1f}B',
            xy=(x[-1], last_val),
            xytext=(0, 10), textcoords='offset points',
            ha='center', va='bottom',
            fontsize=13, fontweight='bold',
            color=POSITIVE_COLOR)

# Y axis
y_ticks = [-5, 0, 5]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${int(v)}B' for v in y_ticks],
                    fontsize=15, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(-6, 8)
ax.tick_params(axis='y', length=0, pad=10)

# X axis — show every 3rd month
tick_positions = list(range(0, len(df), 3))
tick_labels = [df.iloc[i]['label'] for i in tick_positions]
ax.set_xticks([x[i] for i in tick_positions])
ax.set_xticklabels(tick_labels, fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'],
                    rotation=45, ha='right')
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

# Zero line
ax.axhline(y=0, color=COLORS['text_secondary'], alpha=0.5, linewidth=1, zorder=2)

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
        f'{output_dir}/btc_etf_monthly_flow.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()

# Stats
cumulative = df['net_flow_b'].sum()
q1_26 = df[df['month'].str.startswith('2026')]['net_flow_b'].sum()
streak_months = ['2025-11', '2025-12', '2026-01', '2026-02']
streak_total = df[df['month'].isin(streak_months)]['net_flow_b'].sum()

print(f'Done: btc_etf_monthly_flow.png / .svg')
print(f'Cumulative all-time: +${cumulative:.1f}B')
print(f'Q1 2026: ${q1_26:.2f}B')
print(f'4-month outflow streak (Nov-Feb): ${streak_total:.2f}B')
print(f'March 2026: +${last_val}B')
