"""
DeFi TVL (DefiLlama) vs STRC Market Cap (strc.live) overlay.
Dual-axis area chart, four-pillars theme.
Source: image reproduction (DefiLlama TVL + strc.live STRC Market Cap).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG, save_chart

setup_font()

TVL_COLOR = '#2962ff'   # DefiLlama blue
STRC_COLOR = '#e8833a'  # strc.live orange


def gradient_fill(ax, x, y, color, top_alpha=0.55, zorder=2):
    """Vertical gradient area fill: opaque near the line, fading to transparent at baseline."""
    x_num = mdates.date2num(x)
    r, g, b = mcolors.to_rgb(color)
    grad = np.empty((256, 1, 4))
    grad[:, 0, 0] = r
    grad[:, 0, 1] = g
    grad[:, 0, 2] = b
    grad[:, 0, 3] = np.linspace(0, top_alpha, 256)
    ymax = y.max() * 1.05
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_num.min(), x_num.max(), 0, ymax],
                   zorder=zorder, interpolation='bilinear')
    verts = np.column_stack([np.r_[x_num, x_num[::-1]],
                             np.r_[y, np.zeros_like(y)]])
    from matplotlib.patches import Polygon
    clip = Polygon(verts, closed=True, facecolor='none', edgecolor='none')
    ax.add_patch(clip)
    im.set_clip_path(clip)


df = pd.read_csv('outputs/data/tvl_vs_strc_mcap.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')

# --- TVL (left axis, blue area) ---
gradient_fill(ax1, df['date'], df['tvl_b'], TVL_COLOR, top_alpha=0.50, zorder=2)
ax1.plot(df['date'], df['tvl_b'], color=TVL_COLOR, linewidth=2.0, zorder=4)

ax1.set_ylim(0, 200)
y1_ticks = np.arange(0, 201, 50)
ax1.set_yticks(y1_ticks)
ax1.set_yticklabels([f'${int(v)}B' for v in y1_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold', color=TVL_COLOR)

# --- STRC Market Cap (right axis, orange area) ---
ax2 = ax1.twinx()
ax2.set_facecolor('none')
gradient_fill(ax2, df['date'], df['strc_mcap_b'], STRC_COLOR, top_alpha=0.45, zorder=3)
ax2.plot(df['date'], df['strc_mcap_b'], color=STRC_COLOR, linewidth=2.0, zorder=5)

ax2.set_ylim(0, 12)
y2_ticks = np.arange(0, 12.1, 3)
ax2.set_yticks(y2_ticks)
ax2.set_yticklabels([f'${int(v)}B' for v in y2_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold', color=STRC_COLOR)

# --- X axis ---
ax1.set_xlim(df['date'].min(), df['date'].max())
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax1.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'],
                colors=COLORS['text_secondary'],
                length=AXIS_CONFIG['x_tick']['length'],
                width=AXIS_CONFIG['x_tick']['width'])
fig.autofmt_xdate(rotation=45, ha='right')
for lbl in ax1.xaxis.get_majorticklabels():
    lbl.set_fontweight('bold')

# --- Grid / spines ---
ax1.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax1.set_axisbelow(True)
for spine in ax1.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)
ax1.tick_params(axis='y', length=0)
ax2.tick_params(axis='y', length=0)
ax1.margins(x=0)

fig.tight_layout()

out_dir = 'outputs/charts/strategy/strc'
png, svg = save_chart(fig, 'tvl_vs_strc_mcap', out_dir)
print(f'Saved: {png}\n       {svg}')
