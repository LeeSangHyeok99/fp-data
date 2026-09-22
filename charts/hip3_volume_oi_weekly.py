"""
HIP-3 Weekly Volume & Open Interest — two 1:1 (square) stacked-bar charts
Source: ASXN Hyperliquid API (api-hyperliquid.asxn.xyz)
  GET /api/meta/hip3/daily-volume-chart  -> outputs/data/hip3_daily_volume.json
  GET /api/meta/hip3/daily-oi-chart      -> outputs/data/hip3_daily_oi.json
Style: four-pillars, transparent BG, no title/legend/source.

Daily data aggregated to weekly (W-MON): volume = weekly SUM, OI = weekly MEAN
(OI is a level, not a flow). Stacked by deployer; xyz dominates (~92% vol).
Validated: weekly volume peak ~$20.8B, OI peak ~$3.01B.
"""

import sys, json
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG

setup_font()

# Deployer colors — EXACT from the ASXN frontend. Palette `m` in useChartConfig
# assigned by the LEGEND order shown on the dashboard:
#   xyz, vntl, flx, hyna, abcd, cash, km, para
COLOR = {
    'xyz':  '#226b59',   # XYZ            (green)
    'vntl': '#FFFFFF',   # Ventuals       (white)
    'flx':  '#004231',   # Felix Exchange (dark green)
    'hyna': '#C2C2C2',   # HyENA          (light grey)
    'abcd': '#055942',   # ABCDEx         (green)
    'cash': '#838383',   # dreamcash      (grey)
    'km':   '#1B7F66',   # Markets by Kinetiq (teal green)
    'para': '#73928E',   # Paragon        (sage grey)
}


def load_weekly(path, key, agg):
    rows = json.load(open(path))
    recs = []
    for r in rows:
        rec = {'date': pd.Timestamp(r['date'])}
        rec.update(r[key])
        recs.append(rec)
    df = pd.DataFrame(recs).set_index('date').fillna(0.0).sort_index()
    wk = df.resample('W-MON').agg(agg) / 1e9        # -> $B
    order = df.sum().sort_values(ascending=False).index.tolist()
    order = [c for c in order if df[c].sum() > 0]   # drop empty deployers
    return wk, order


def draw(path, key, agg, ymax, ystep, fname):
    wk, order = load_weekly(path, key, agg)
    weeks = wk.index
    fig, ax = plt.subplots(figsize=(7, 7), dpi=150)

    bottom = np.zeros(len(weeks))
    for dep in order:
        ax.bar(weeks, wk[dep].values, width=4.6, bottom=bottom,
               color=COLOR.get(dep, '#787b86'), zorder=3, linewidth=0)
        bottom += wk[dep].values

    ax.set_ylim(0, ymax)
    ax.yaxis.set_major_locator(MultipleLocator(ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}B"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(weeks[0] - pd.Timedelta(days=6), weeks[-1] + pd.Timedelta(days=6))

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
    ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'],
                   pad=AXIS_CONFIG['x_tick']['pad'], rotation=45,
                   colors=AXIS_CONFIG['x_tick']['color'])
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    fig.tight_layout()

    png, _ = save_chart(fig, fname, 'outputs/charts/hyperliquid/hip3')
    plt.close(fig)
    print('saved:', png, '| peak total $%.2fB' % bottom.max())


draw('outputs/data/hip3_daily_volume.json', 'dex_volumes', 'sum',
     ymax=21, ystep=5, fname='hip3_weekly_volume')      # 0,5,10,15,20
draw('outputs/data/hip3_daily_oi.json', 'dex_oi', 'mean',
     ymax=3.2, ystep=1, fname='hip3_weekly_oi')          # 0,1,2,3
