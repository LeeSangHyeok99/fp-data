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
df = pd.read_csv('/Users/ijaheun/Desktop/morpho-unlock-schedule-2026-03-12.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Resample to weekly for cleaner chart (daily is too dense for 6+ years)
df = df.set_index('Date').resample('W').last().reset_index()

# Convert to millions
cols = ['Contributors', 'Founders', 'Early Contributors', 'Strategic Partners', 'Rewards']
for col in cols:
    df[col] = df[col] / 1e6

output_dir = 'outputs/charts/morpho'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Chart: Stacked Area - Morpho Token Unlock Schedule
# =============================================================================
setup_font()

# Morpho brand-inspired palette (blue tones + complementary)
area_colors = {
    'Strategic Partners': '#004EC3',   # Morpho primary blue
    'Founders': '#2171D6',             # Lighter blue
    'Rewards': '#5BA0E8',              # Light blue
    'Contributors': '#8CC4F5',         # Pale blue
    'Early Contributors': '#B8DDFB',   # Very pale blue
}

# Stack order (bottom to top): largest to smallest for readability
stack_order = ['Strategic Partners', 'Founders', 'Rewards', 'Contributors', 'Early Contributors']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Stacked area
y_stack = np.zeros(len(df))
for col in stack_order:
    ax.fill_between(df['Date'], y_stack, y_stack + df[col].values,
                    color=area_colors[col], alpha=0.85, linewidth=0, zorder=2)
    ax.plot(df['Date'], y_stack + df[col].values,
            color=area_colors[col], linewidth=0.5, alpha=0.6, zorder=3)
    y_stack += df[col].values

# Today marker
today = pd.Timestamp('2026-03-12')
today_total = df.loc[df['Date'] <= today].iloc[-1][stack_order].sum()
ax.axvline(x=today, color=COLORS['text_secondary'], alpha=0.6,
           linestyle='--', linewidth=1, zorder=4)
ax.text(today, today_total + 15, 'Today', ha='center', va='bottom',
        fontsize=13, fontweight='bold', color=COLORS['text_secondary'], zorder=5)

# Y-axis
y_ticks = [0, 100, 200, 300, 400, 500]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}M' for v in y_ticks],
                   fontsize=16, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=15)
ax.set_ylim(0, 550)

# X-axis
years = pd.date_range('2023-01-01', '2029-01-01', freq='YS')
ax.set_xticks(years)
ax.set_xticklabels([str(y.year) for y in years],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=6, width=1, pad=10, rotation=45, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.set_xlim(df['Date'].min(), df['Date'].max())

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Endpoint labels (right side)
y_acc = 0
for col in stack_order:
    val = df[col].iloc[-1]
    y_mid = y_acc + val / 2
    if val > 5:  # Only label significant portions
        label = col.replace('Early Contributors', 'Early').replace('Strategic Partners', 'Strategic')
        ax.text(df['Date'].iloc[-1] + pd.Timedelta(days=15), y_mid,
                f'{label}\n{val:.0f}M', va='center', ha='left',
                fontsize=11, fontweight='bold', color=area_colors[col], zorder=5)
    y_acc += val

fig.tight_layout()
fig.savefig(f'{output_dir}/morpho_unlock_schedule.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/morpho_unlock_schedule.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print("Chart saved: Morpho Unlock Schedule")
print(f"\nFinal unlocked (2029-03): {y_acc:.0f}M MORPHO")
for col in stack_order:
    val = df[col].iloc[-1]
    pct = val / y_acc * 100
    print(f"  {col}: {val:.0f}M ({pct:.1f}%)")

# Current unlock status
now_row = df.loc[df['Date'] <= today].iloc[-1]
now_total = now_row[stack_order].sum()
print(f"\nCurrent unlock (2026-03-12): {now_total:.0f}M MORPHO ({now_total/y_acc*100:.0f}% of total)")
