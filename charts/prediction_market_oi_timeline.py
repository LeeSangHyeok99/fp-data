import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (setup_font, COLORS, DPI, GRID_CONFIG,
                    area_glow, endpoint_dot)

# =============================================================================
# Data
# =============================================================================
print("Loading data...")
df = pd.read_csv('outputs/data/kalshi_polymarket_merged.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

theme_map = {
    'Sports': 'Sports',
    'Politics': 'Politics',
    'Economics': 'Macro',
    'Crypto': 'Crypto',
    'Culture': 'Culture',
    'STEM': 'STEM',
    'Financials': 'Macro',
}
df['theme'] = df['category'].map(theme_map).fillna('Other')

# Daily aggregates
daily_total = df.groupby('date')['open_interest_usd'].sum().reset_index()
daily_total['date'] = pd.to_datetime(daily_total['date'])
daily_total['oi_m'] = daily_total['open_interest_usd'] / 1e6

daily_theme = df.groupby(['date', 'theme'])['open_interest_usd'].sum().reset_index()
daily_theme['date'] = pd.to_datetime(daily_theme['date'])
theme_pivot = daily_theme.pivot_table(index='date', columns='theme', values='open_interest_usd', aggfunc='sum').fillna(0) / 1e6

daily_platform = df.groupby(['date', 'source'])['open_interest_usd'].sum().reset_index()
daily_platform['date'] = pd.to_datetime(daily_platform['date'])
plat_pivot = daily_platform.pivot_table(index='date', columns='source', values='open_interest_usd', aggfunc='sum').fillna(0) / 1e6

# Filter 2024+
START = pd.Timestamp('2024-01-01')
daily_total = daily_total[daily_total['date'] >= START]
theme_pivot = theme_pivot[theme_pivot.index >= START]
plat_pivot = plat_pivot[plat_pivot.index >= START]

output_dir = 'outputs/charts/prediction_markets'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Events
events = [
    ('2024-06-01', 'CFTC proposes\nevent contract ban'),
    ('2024-09-15', 'Kalshi wins\nCFTC lawsuit'),
    ('2024-11-05', '2024\nUS Election'),
    ('2025-05-05', 'CFTC drops\nKalshi appeal'),
    ('2025-11-25', 'Polymarket\nUS re-entry'),
    ('2026-01-29', 'CFTC withdraws\nban proposal'),
    ('2026-03-12', 'CFTC Advisory\n+ ANPRM'),
]
events = [(pd.Timestamp(d), l) for d, l in events]

def add_events(ax, y_max, alternate=True):
    """Add event markers with alternating top/bottom labels."""
    for i, (date, label) in enumerate(events):
        ax.axvline(x=date, color='#d1d4dc', alpha=0.25, linestyle='-', linewidth=0.7, zorder=1)
        if alternate:
            if i % 2 == 0:
                y_pos = y_max * 1.02
                va = 'bottom'
            else:
                y_pos = y_max * 0.82
                va = 'bottom'
        else:
            y_pos = y_max * 1.02
            va = 'bottom'
        ax.annotate(label, xy=(date, y_pos),
                    fontsize=7.5, fontweight='bold', color='#d1d4dc',
                    ha='center', va=va, zorder=4, alpha=0.8)

# =============================================================================
# Chart 1: Total OI with area glow
# =============================================================================
setup_font()

TOTAL_C = '#5470c6'

fig, ax = plt.subplots(figsize=(14, 5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

dates = daily_total['date']
oi = daily_total['oi_m']

# Area glow
area_glow(ax, dates, oi, color=TOTAL_C, n_layers=40, max_alpha=0.2, power=2.0)
ax.plot(dates, oi, color=TOTAL_C, linewidth=1.5, zorder=4)
endpoint_dot(ax, dates.iloc[-1], oi.iloc[-1], color=TOTAL_C, size=40)

# Events
add_events(ax, oi.max())

# Y-axis
y_ticks = [0, 250, 500, 750, 1000]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}M' for v in y_ticks],
                   fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=12)
ax.set_ylim(0, oi.max() * 1.2)

# X-axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.tick_params(axis='x', labelsize=11, pad=8, length=0, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), fontweight='bold', ha='right', rotation=45)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_oi_timeline.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_oi_timeline.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 1 saved: Total OI Timeline")

# =============================================================================
# Chart 2: Top 4 themes multi-line
# =============================================================================
setup_font()

theme_colors = {
    'Sports':   '#91cc75',
    'Politics': '#5470c6',
    'Macro':    '#73c0de',
    'Crypto':   '#f7931a',
}

fig, ax = plt.subplots(figsize=(14, 5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

for theme, color in theme_colors.items():
    if theme in theme_pivot.columns:
        vals = theme_pivot[theme]
        ax.plot(theme_pivot.index, vals, color=color, linewidth=1.8, zorder=4)
        ax.fill_between(theme_pivot.index, 0, vals, color=color, alpha=0.06, linewidth=0, zorder=2)
        endpoint_dot(ax, theme_pivot.index[-1], vals.iloc[-1], color=color, size=35)

# Events
theme_max = theme_pivot[list(theme_colors.keys())].max().max()
add_events(ax, theme_max)

# Y-axis
y_ticks = [0, 100, 200, 300, 400]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}M' for v in y_ticks],
                   fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=12)
ax.set_ylim(0, theme_max * 1.25)

# X-axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.tick_params(axis='x', labelsize=11, pad=8, length=0, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), fontweight='bold', ha='right', rotation=45)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/prediction_market_themes_timeline.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/prediction_market_themes_timeline.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 2 saved: Theme Lines Timeline")

# =============================================================================
# Chart 3: Kalshi vs Polymarket
# =============================================================================
setup_font()

KALSHI_C = '#5470c6'
POLY_C = '#91cc75'

fig, ax = plt.subplots(figsize=(14, 5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

for col, color in [('Kalshi', KALSHI_C), ('Polymarket', POLY_C)]:
    if col in plat_pivot.columns:
        vals = plat_pivot[col]
        ax.plot(plat_pivot.index, vals, color=color, linewidth=1.8, zorder=4)
        ax.fill_between(plat_pivot.index, 0, vals, color=color, alpha=0.08, linewidth=0, zorder=2)
        endpoint_dot(ax, plat_pivot.index[-1], vals.iloc[-1], color=color, size=40)

# Events
plat_max = plat_pivot.max().max()
add_events(ax, plat_max)

# Y-axis
y_ticks = [0, 150, 300, 450, 600]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}M' for v in y_ticks],
                   fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=12)
ax.set_ylim(0, plat_max * 1.25)

# X-axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.tick_params(axis='x', labelsize=11, pad=8, length=0, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), fontweight='bold', ha='right', rotation=45)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_timeline.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/kalshi_vs_polymarket_timeline.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 3 saved: Kalshi vs Polymarket Timeline")

# Stats
print(f"\nPeak Total OI: ${daily_total['oi_m'].max():.0f}M ({daily_total.loc[daily_total['oi_m'].idxmax(), 'date'].strftime('%Y-%m-%d')})")
print(f"Current Total OI: ${daily_total['oi_m'].iloc[-1]:.0f}M")
