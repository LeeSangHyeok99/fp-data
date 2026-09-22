"""
HL Weekend Move vs Actual Monday Open Gap — Korean stocks (4 grouped-bar charts)
Source: Hyperliquid API (HIP-3 daily candles), Yahoo Finance
        (KRX: 005930.KS / 000660.KS / 005380.KS, NYSE: EWY)
Data:   ~/Downloads/hl_weekend_korean_stocks (1).csv  (real, 62 rows)
Style:  four-pillars, transparent BG, no title/legend/source.

Per asset, by weekend: blue = HL weekend move %, second bar = actual Monday
open gap % (grey if direction matched, red if wrong). Zero reference line.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG, COLORS

setup_font()

BLUE = '#4d8fd6'    # HL weekend move
GREY = '#c7ccd1'    # actual gap, direction matched
RED  = '#b5403a'    # actual gap, wrong direction

CSV = "/Users/a./Downloads/hl_weekend_korean_stocks (1).csv"
df = pd.read_csv(CSV)
# Drop incomplete weeks (no actual Monday yet -> NaN). EWY's last week (06-05)
# is unsettled, so EWY is 7/13, not 7/14.
df = df.dropna(subset=['direction_match', 'actual_gap_pct']).reset_index(drop=True)
df['week'] = pd.to_datetime(df['weekend_fri_date'])

# Per-asset clean y-axis (ylim, tick list)
AXES = {
    'SMSN':    (-12, 8,  [-10, -5, 0, 5]),
    'SKHX':    (-12, 10, [-10, -5, 0, 5, 10]),
    'HYUNDAI': (-12, 4,  [-12, -8, -4, 0, 4]),
    'EWY':     (-4, 8,   [-4, 0, 4, 8]),
}
FNAME = {'SMSN': 'samsung', 'SKHX': 'sk_hynix',
         'HYUNDAI': 'hyundai', 'EWY': 'ewy'}

out_dir = 'outputs/charts/hyperliquid/hip3'

for asset, g in df.groupby('asset'):
    g = g.sort_values('week').reset_index(drop=True)
    x = np.arange(len(g))
    move = g['hl_wknd_move_pct'].values
    gap = g['actual_gap_pct'].values
    gap_colors = [GREY if m == 1 else RED for m in g['direction_match'].values]

    fig, ax = plt.subplots(figsize=(10.67, 4.0), dpi=150)
    w = 0.4
    ax.bar(x - w / 2, move, width=w, color=BLUE, zorder=3, linewidth=0)
    ax.bar(x + w / 2, gap, width=w, color=gap_colors, zorder=3, linewidth=0)

    # zero line
    ax.axhline(0, color=COLORS['text_secondary'], linewidth=1.0, alpha=0.7, zorder=2)

    ylo, yhi, yticks = AXES[asset]
    ax.set_ylim(ylo, yhi)
    ax.yaxis.set_major_locator(FixedLocator(yticks))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))

    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b %d') for d in g['week']])
    ax.set_xlim(-0.7, len(g) - 0.3)

    # four-pillars styling
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'],
                   pad=AXIS_CONFIG['y_tick']['pad'], length=0,
                   colors=AXIS_CONFIG['y_tick']['color'])
    ax.tick_params(axis='x', labelsize=13, pad=8, rotation=45,
                   colors=AXIS_CONFIG['x_tick']['color'])
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    fig.tight_layout()

    png, _ = save_chart(fig, f'hl_weekend_move_vs_gap_{FNAME[asset]}', out_dir)
    plt.close(fig)
    m = int(g['direction_match'].sum())
    print(f"saved: {png}  ({asset}: {m}/{len(g)} match)")
