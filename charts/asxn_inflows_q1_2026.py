import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/asxn_inflows_q1_2026.csv', parse_dates=['date'])

POSITIVE = '#22c55e'
NEGATIVE = '#ef4444'
ORANGE = '#ff8c00'

setup_font()
fig, ax_left = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax_left.set_facecolor('none')

# Bars: daily net inflow in $M
inflow_m = df['inflow'] / 1e6
bar_colors = [POSITIVE if v >= 0 else NEGATIVE for v in inflow_m]
ax_left.bar(df['date'], inflow_m, color=bar_colors, width=0.85, zorder=2, linewidth=0)

# Zero line
ax_left.axhline(0, color=COLORS['text_secondary'], linewidth=0.8, alpha=0.5, zorder=1)

# Right axis: cumulative net inflow in $B
ax_right = ax_left.twinx()
ax_right.set_facecolor('none')
cum_b = df['cumulative_inflow'] / 1e9
ax_right.plot(df['date'], cum_b, color=ORANGE, linewidth=2.2, zorder=3)

# Left Y axis: -$100M to $100M (match reference)
ax_left.set_ylim(-100, 100)
ax_left.set_yticks([-100, -50, 0, 50, 100])
def fmt_m(v, _):
    if v == 0:
        return '$0M'
    sign = '-' if v < 0 else ''
    return f'{sign}${abs(v):.0f}M'

ax_left.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))

# Right Y axis: $3.60B to $4.20B (5 ticks at 0.15B step)
ax_right.set_ylim(3.60, 4.20)
ax_right.set_yticks([3.60, 3.75, 3.90, 4.05, 4.20])
ax_right.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.2f}B'))

# X axis: month start ticks
month_starts = pd.date_range(start='2026-01-01', end='2026-04-01', freq='MS')
ax_left.set_xticks(month_starts)
ax_left.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax_left.set_xlim(df['date'].iloc[0] - pd.Timedelta(days=2), pd.Timestamp('2026-04-02'))

apply_style(fig, ax_left, 'bar')

# Hide right spine but keep ticks
for spine in ax_right.spines.values():
    spine.set_visible(False)

# Tick sizing
ax_left.tick_params(axis='y', labelsize=18, length=0, colors=COLORS['text_secondary'])
ax_right.tick_params(axis='y', labelsize=18, length=0, colors=COLORS['text_secondary'])
ax_left.tick_params(axis='x', labelsize=18, length=0, pad=20, colors=COLORS['text_secondary'])

# Grid only on left axis (matches data axis)
ax_left.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax_left.set_axisbelow(True)
ax_right.grid(False)

output_dir = 'outputs/charts/hyperliquid/metrics'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/asxn_inflows_q1_2026.png"
svg_path = f"{output_dir}/asxn_inflows_q1_2026.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
