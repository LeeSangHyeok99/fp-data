"""PAXG & XAUT, % of supply active in DeFi (90 days). Four Pillars theme.

Reference: DefiLlama newsletter chart, PAXG vs XAUT % of supply active in DeFi.
Data: DefiLlama RWA API (REAL values), reference window Jan 5 - Apr 6 2026 (~90 days).
  Endpoint: https://defillama.com/_next/data/{buildId}/rwa/asset/{PAXG,XAUT}.json
    -> pageProps.asset.chartDataset.source, %active = DeFi Active TVL / Onchain Mcap
  (buildId from page __NEXT_DATA__.buildId; Cloudflare-gated, fetch via real browser.)
  Matches reference exactly: XAUT 2.47% -> 6.16% spike (31 Jan 2026: $156.5M/$2.541B)
  -> 4.95%; PAXG 1.39% -> 0.95%. The reference window is 2026 (not 2025).
  Endpoint: https://defillama.com/_next/data/{buildId}/rwa/asset/{PAXG,XAUT}.json
    -> pageProps.asset.chartDataset.source (DeFi Active TVL, Active Mcap, Onchain Mcap)
  Metric: % of supply active in DeFi = DeFi Active TVL / Onchain Mcap * 100
  (buildId from page __NEXT_DATA__.buildId; site is Cloudflare-gated, fetch via
   a real browser, not curl.)
  NB: The original reference screenshot (Jan-Apr 2025) is NOT accurate anymore.
  DefiLlama revised its historical DeFi Active TVL down (XAUT ~10x: the screenshot
  showed ~2.8% for Jan 2025 but the real value is ~0.29%). This chart uses the
  current live window, which is what real DefiLlama data actually shows.
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
from config import create_figure, apply_style, save_chart

XAUT_COLOR = "#4568e0"   # blue
PAXG_COLOR = "#e5352b"   # red


def gradient_fill(ax, x, y, color, ymax, alpha_top=0.45):
    """Vertical gradient fill from the line down to 0, fading out."""
    xnum = mdates.date2num(x)
    r, g, b = mcolors.to_rgb(color)
    grad = np.empty((256, 1, 4))
    for i in range(256):
        frac = i / 255                      # 0 bottom, 1 top
        grad[i, 0] = [r, g, b, alpha_top * frac]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[xnum.min(), xnum.max(), 0, ymax],
                   zorder=2, interpolation='bilinear')
    verts = np.column_stack([np.r_[xnum, xnum[::-1]],
                             np.r_[y, np.zeros_like(y)]])
    from matplotlib.patches import Polygon
    clip = Polygon(verts, closed=True, facecolor='none', edgecolor='none')
    ax.add_patch(clip)
    im.set_clip_path(clip)


df = pd.read_csv('outputs/data/paxg_xaut_defi_supply_share.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)
dates = df['date']

fig, ax = create_figure('area')

YMAX = 7
gradient_fill(ax, dates, df['xaut'].values, XAUT_COLOR, YMAX, alpha_top=0.45)
gradient_fill(ax, dates, df['paxg'].values, PAXG_COLOR, YMAX, alpha_top=0.45)
ax.plot(dates, df['xaut'], color=XAUT_COLOR, linewidth=2.0, zorder=4)
ax.plot(dates, df['paxg'], color=PAXG_COLOR, linewidth=2.0, zorder=4)

# Y axis: 0-7%, clean step of 2 (matches reference)
ax.set_ylim(0, YMAX)
ax.set_yticks([0, 2, 4, 6])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{int(v)}%'))

# X axis: monthly ticks in Mon YYYY
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(dates.iloc[0], dates.iloc[-1])

apply_style(fig, ax, 'area')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

out_dir = 'outputs/charts/rwa/gold'
save_chart(fig, 'paxg_xaut_defi_supply_share', out_dir)
plt.close(fig)
print('saved to', out_dir)
