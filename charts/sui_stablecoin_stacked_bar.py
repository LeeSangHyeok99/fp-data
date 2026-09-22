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
df = pd.read_csv('/tmp/sui_stablecoins.csv')
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= '2024-03-01']
# Convert to millions
for col in ['USDC', 'USDT', 'FDUSD', 'BUCK', 'USDY', 'AUSD']:
    df[col] = df[col] / 1e6

# Total
df['total'] = df[['USDC', 'USDT', 'FDUSD', 'BUCK', 'USDY', 'AUSD']].sum(axis=1)

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

SUI_BLUE = '#4DA2FF'

x = df['date']
y = df['total'].values

# Fill under line
ax.fill_between(x, y, color=SUI_BLUE, alpha=0.15)
# Line
ax.plot(x, y, color=SUI_BLUE, linewidth=1.5)

# ══════════════════════════════════════════════════
# Y-axis
# ══════════════════════════════════════════════════
ax.set_ylim(0, 1200)
ax.set_yticks([0, 300, 600, 900, 1200])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'${x/1000:.1f}B'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min() - pd.Timedelta(days=5),
            df['date'].max() + pd.Timedelta(days=5))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'sui_stablecoin_stacked_bar',
                                'outputs/charts/sui')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
