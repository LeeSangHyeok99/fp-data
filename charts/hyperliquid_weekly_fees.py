import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import json
from datetime import datetime

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG, gradient_rounded_bar

output_dir = 'outputs/charts/hyperliquid/revenue'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data: Load and aggregate daily fees to weekly
# =============================================================================
with open('outputs/data/hyperliquid_daily_fees_raw.json') as f:
    raw = json.load(f)

daily = raw['totalDataChart']
df = pd.DataFrame(daily, columns=['timestamp', 'fees'])
df['date'] = pd.to_datetime(df['timestamp'], unit='s')
df['fees_m'] = df['fees'] / 1e6

# Aggregate to ISO weeks (Mon-Sun)
df['week'] = df['date'].dt.isocalendar().week.astype(int)
df['year'] = df['date'].dt.isocalendar().year.astype(int)
df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='D')

weekly = df.groupby('week_start').agg(
    fees=('fees', 'sum'),
    days=('fees', 'count')
).reset_index()

# Only keep full weeks (7 days) except allow the most recent partial week
weekly = weekly[(weekly['days'] >= 7) | (weekly.index == weekly.index[-1])].copy()
# Drop last if partial (less than 5 days)
if weekly.iloc[-1]['days'] < 5:
    weekly = weekly.iloc[:-1].copy()

weekly['fees_m'] = weekly['fees'] / 1e6
weekly['week_label'] = weekly['week_start'].dt.strftime('%b %Y')

# =============================================================================
# Chart: Weekly Fees Bar Chart
# =============================================================================
setup_font()

HL_GREEN = '#50e3c2'

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(weekly))
bar_width = 0.7

# Find the record week
record_idx = weekly['fees_m'].idxmax()
record_week_pos = list(weekly.index).index(record_idx)

for i, (idx, row) in enumerate(weekly.iterrows()):
    color = '#FFFFFF' if i == record_week_pos else HL_GREEN
    alpha = 1.0 if i == record_week_pos else 0.85
    gradient_rounded_bar(ax, x[i], bar_width, row['fees_m'], color, alpha=alpha)

# Record week annotation
record_val = weekly.loc[record_idx, 'fees_m']
ax.annotate(
    f'${record_val:.1f}M',
    xy=(record_week_pos, record_val),
    xytext=(0, 12),
    textcoords='offset points',
    ha='center', va='bottom',
    fontsize=14, fontweight='bold',
    color='#FFFFFF',
)

# Y axis
max_val = weekly['fees_m'].max()
y_max = np.ceil(max_val / 5) * 5
tick_step = 5
y_ticks = np.arange(0, y_max + tick_step, tick_step)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${int(v)}M' for v in y_ticks],
                    fontsize=18, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, y_max + 3)

# X axis - show every 4th week
tick_positions = list(range(0, len(weekly), 4))
tick_labels = [weekly.iloc[i]['week_start'].strftime('%b %Y') for i in tick_positions]
ax.set_xticks([x[i] for i in tick_positions])
ax.set_xticklabels(tick_labels, fontsize=16, fontweight='bold',
                    color=COLORS['text_secondary'],
                    rotation=45, ha='right')

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0)

fig.tight_layout()

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hyperliquid_weekly_fees.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()
print('Done: hyperliquid_weekly_fees.png / .svg')
print(f'Record week: {weekly.loc[record_idx, "week_start"].strftime("%Y-%m-%d")} = ${record_val:.2f}M')
print(f'Total weeks: {len(weekly)}')
print(f'All-time total: ${weekly["fees_m"].sum():.1f}M')
