"""
HIP-4 Daily Volume by Deployer (Aug 2026), HRC dark theme.
데이터/구성은 charts/hip4_daily_volume_by_deployer.py와 동일, 팔레트만 HRC.
"""

import sys

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI, GRID_CONFIG, FIGURE_SIZES, save_chart, setup_font
from hip4_hrc_palette import BODY, HYPERLIQUID, NOTE, OUTCOME, SKEW

COLOR = {
    'hyperliquid_musd': HYPERLIQUID,
    'outcome_musd': OUTCOME,
    'skew_musd': SKEW,
}

df = pd.read_csv('outputs/data/hip4_daily_volume_by_deployer.csv',
                 parse_dates=['date'])

setup_font()
fig, ax = plt.subplots(figsize=FIGURE_SIZES['stacked_bar'], dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 일별 바는 vlines로 (bar는 픽셀 반올림으로 폭이 들쭉날쭉해진다)
SLICES = 24
TOP_LIGHTEN = 0.14
SAT = 1.18


def shade(color, t):
    h, sat, v = mcolors.rgb_to_hsv(mcolors.to_rgb(color))
    r, g, b = mcolors.hsv_to_rgb((h, min(sat * SAT, 1.0), v))
    k = TOP_LIGHTEN * t
    return (r + (1 - r) * k, g + (1 - g) * k, b + (1 - b) * k)


bottoms = np.zeros(len(df))
for col, color in COLOR.items():
    vals = df[col].values
    tops = bottoms + vals
    edges = bottoms + np.outer(np.linspace(0, 1, SLICES + 1), vals)
    pad = vals / SLICES * 0.5
    for i in range(SLICES):
        lo, hi = edges[i], edges[i + 1] + (pad if i < SLICES - 1 else 0)
        m = vals > 0
        ax.vlines(df['date'][m], lo[m], hi[m], color=shade(color, i / (SLICES - 1)),
                  linewidth=19, zorder=3)
    bottoms = tops

ax.set_ylim(0, 2.0)
ax.yaxis.set_major_locator(mticker.FixedLocator([0, 0.5, 1.0, 1.5, 2.0]))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: '$0' if v == 0 else f'${v:.1f}M'))

ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
            df['date'].max() + pd.Timedelta(days=1))
ticks = [d for d in df['date'] if d.day in (1, 5, 10, 15, 20, 25, 31)]
ax.xaxis.set_major_locator(mticker.FixedLocator(mdates.date2num(ticks)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

# 8/29 퍼미션리스 배포 개시
split = df['date'].min() + pd.Timedelta(days=27, hours=12)
ax.axvline(split, color=NOTE, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
ax.text(split - pd.Timedelta(hours=6), 1.92,
        'Aug 29\nPermissionless\nDeployment Opens',
        color=NOTE, fontsize=13, fontweight='bold',
        ha='right', va='top', linespacing=1.5)

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.grid(axis='x', visible=False)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=17, pad=12, length=0, colors=BODY)
ax.tick_params(axis='x', labelsize=15, pad=10, length=6, width=1, colors=BODY)
for lbl in ax.get_xticklabels():
    lbl.set_rotation(45)
    lbl.set_ha('right')
    lbl.set_rotation_mode('anchor')

fig.tight_layout()
png, svg = save_chart(fig, 'hip4_daily_volume_by_deployer_hrc',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
