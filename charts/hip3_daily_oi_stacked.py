import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    COLORS,
    DPI,
    GRID_CONFIG,
    save_chart,
    setup_font,
)


# ══════════════════════════════════════════════════
# Data (ASXN API: /api/meta/hip3/daily-oi-chart?timeframe=all)
# Per-deployer daily OI, Oct 2025 → Apr 2026
# ══════════════════════════════════════════════════
raw = json.loads(Path('/Users/ijaheun/Desktop/Project/data/outputs/data/hip3_daily_oi_chart_api.json').read_text())

DEPLOYERS = ['xyz', 'cash', 'hyna', 'vntl', 'km', 'flx', 'para', 'abcd']

records = []
for entry in raw:
    row = {'date': entry['date']}
    dex = entry.get('dex_oi', {})
    for key in DEPLOYERS:
        row[key] = dex.get(key, 0) / 1e6  # to $M
    records.append(row)

df = pd.DataFrame(records)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# ══════════════════════════════════════════════════
# Colors (brand-ish, distinct, dark-mode readable)
# ══════════════════════════════════════════════════
COLOR_MAP = {
    'xyz':  '#2dd4bf',  # deep Hyperliquid teal (main)
    'cash': '#ffffff',  # pure white
    'hyna': '#047857',  # dark emerald
    'vntl': '#9ca3af',  # mid gray
    'km':   '#0f9488',  # deep teal
    'flx':  '#d1d5db',  # cool silver
    'para': '#065f46',  # darkest forest green
    'abcd': '#4b5563',  # slate gray
}

# ══════════════════════════════════════════════════
# Figure (stacked bar)
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(700/150, 500/150), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bottoms = np.zeros(len(df))
for dep in DEPLOYERS:
    vals = df[dep].values
    ax.bar(
        df['date'],
        vals,
        bottom=bottoms,
        width=0.78,
        color=COLOR_MAP[dep],
        linewidth=0,
        align='center',
    )
    bottoms = bottoms + vals

totals = bottoms.copy()

# ══════════════════════════════════════════════════
# Y-axis: 0 → $2.5B (step $0.5B)
# ══════════════════════════════════════════════════
y_max = 2500  # $M
ax.set_ylim(0, y_max)
y_ticks = [0, 500, 1000, 1500, 2000, 2500]
ax.yaxis.set_major_locator(mticker.FixedLocator(y_ticks))


def fmt_y(x, _):
    if x == 0:
        return '$0B'
    return f'${x / 1000:.1f}B'


ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_y))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.set_xlim(df['date'].min() - pd.Timedelta(days=3),
            df['date'].max() + pd.Timedelta(days=3))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# ══════════════════════════════════════════════════
# Style (grid, spines, tick colors)
# ══════════════════════════════════════════════════
ax.grid(
    True,
    axis='y',
    color=GRID_CONFIG['color'],
    alpha=GRID_CONFIG['alpha'],
    linestyle=GRID_CONFIG['linestyle'],
    linewidth=GRID_CONFIG['linewidth'],
)
ax.grid(axis='x', visible=False)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=16, pad=12, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=14, pad=10, length=6, width=1,
               colors=COLORS['text_secondary'])

for lbl in ax.get_xticklabels():
    lbl.set_fontweight('bold')
    lbl.set_ha('center')
for lbl in ax.get_yticklabels():
    lbl.set_fontweight('bold')

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
out_dir = Path('outputs/charts/hyperliquid/hip3')
out_dir.mkdir(parents=True, exist_ok=True)
png_path = out_dir / 'hip3_daily_oi_stacked.png'
svg_path = out_dir / 'hip3_daily_oi_stacked.svg'
fig.set_size_inches(700/150, 500/150)
fig.savefig(png_path, dpi=150, facecolor='none', transparent=True)
fig.savefig(svg_path, dpi=150, facecolor='none', transparent=True, format='svg')
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# ══════════════════════════════════════════════════
# Diagnostics
# ══════════════════════════════════════════════════
print(f"\nDate range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Rows: {len(df)}")
last = df.iloc[-1]
total_last = sum(last[d] for d in DEPLOYERS)
print(f"\nLast day ({last['date'].date()}) OI breakdown:")
for dep in DEPLOYERS:
    v = last[dep]
    pct = v / total_last * 100 if total_last > 0 else 0
    print(f"  {dep}: ${v:,.2f}M ({pct:.2f}%)")
print(f"  TOTAL: ${total_last:,.2f}M")

peak_idx = totals.argmax()
print(f"\nPeak OI: ${totals[peak_idx]:,.0f}M on {df.iloc[peak_idx]['date'].date()}")
