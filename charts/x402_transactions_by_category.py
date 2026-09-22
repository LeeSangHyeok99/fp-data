import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
csv_path = '/Users/ijaheun/Downloads/x402 Transactions by Category (Adjusted).csv'
df = pd.read_csv(csv_path)
df['DateTime'] = pd.to_datetime(df['DateTime'])
df = df.fillna(0)

# Filter: Token Launches first appearance (Oct 19, 2025) to early March 2026
df = df[(df['DateTime'] >= '2025-10-19') & (df['DateTime'] <= '2026-03-08')].reset_index(drop=True)

# Stack order (bottom → top), matches original chart
stack_cols = [
    'Agent to Agent Services',
    'Infrastructure & Utilities',
    'Data as a Service',
    'AI Generated Content',
    'Token Launches & Fair Mints',
    'Premium Content & Paywalls',
    'Other',
]

CATEGORY_COLORS = {
    'Agent to Agent Services':     '#4a90e2',
    'Infrastructure & Utilities':  '#50e3c2',
    'Data as a Service':           '#f5a623',
    'AI Generated Content':        '#b06bff',
    'Token Launches & Fair Mints': '#ec4899',
    'Premium Content & Paywalls':  '#f5d34a',
    'Other':                       '#9ca3af',
}

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

dates = df['DateTime']
bottom = np.zeros(len(df))
bar_width = 0.85

for col in stack_cols:
    values = df[col].values
    ax.bar(dates, values, bottom=bottom, width=bar_width,
           color=CATEGORY_COLORS[col], linewidth=0, zorder=2)
    bottom += values

# ══════════════════════════════════════════════════
# Y-axis
# ══════════════════════════════════════════════════
ax.set_ylim(0, 2_000_000)
ax.set_yticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{x/1_000_000:.1f}M'
))
ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
               colors=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(dates.min() - pd.Timedelta(days=2),
            dates.max() + pd.Timedelta(days=2))
ax.tick_params(axis='x', labelsize=12, pad=8, length=8, width=1.5,
               direction='out', bottom=True, top=False,
               color=COLORS['text_secondary'],
               labelcolor=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontweight='bold')

# ══════════════════════════════════════════════════
# Grid & spines
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine_name, spine in ax.spines.items():
    if spine_name == 'bottom':
        spine.set_visible(True)
        spine.set_color(COLORS['text'])
        spine.set_linewidth(1.2)
    else:
        spine.set_visible(False)

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'x402_transactions_by_category',
                                'outputs/charts/x402/category')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
print(f"Date range: {df['DateTime'].min().date()} → {df['DateTime'].max().date()}")
print(f"Days: {len(df)}")
