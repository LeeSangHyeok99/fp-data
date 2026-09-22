import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/asxn_af_buyback_q1_2026.csv', parse_dates=['date'])

# Hyperliquid brand mint family
HYPE_MINT = '#50e3c2'       # 라인: avg buyback price
HYPE_MINT_LIGHT = '#a8d8c5' # 점: daily close (옅은 민트)

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Avg buyback price (line, brighter mint)
ax.plot(
    df['date'], df['avg_buyback_price'],
    color=HYPE_MINT, linewidth=2.0, zorder=2,
)
# Daily close (markers only, lighter mint)
ax.plot(
    df['date'], df['close_usd'],
    color=HYPE_MINT_LIGHT, linewidth=0, zorder=3,
    marker='o', markersize=8, markeredgecolor='none',
)

# Y axis: tighter range so data uses more vertical space
ax.set_ylim(18, 45)
ax.set_yticks([20, 25, 30, 35, 40, 45])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}'))

# X axis: month start ticks
month_starts = pd.date_range(start='2026-01-01', end='2026-04-01', freq='MS')
ax.set_xticks(month_starts)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].iloc[0] - pd.Timedelta(days=2), pd.Timestamp('2026-04-02'))

apply_style(fig, ax, 'line')

ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0, pad=20)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/hyperliquid/revenue'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/asxn_af_buyback_q1_2026.png"
svg_path = f"{output_dir}/asxn_af_buyback_q1_2026.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
