"""
HIP-4 Daily Volume Since Mainnet Launch (2026-05-02 ~ 09-01), HRC dark theme.
데이터/구성은 charts/hip4_daily_volume_since_launch.py와 동일, 팔레트만 HRC.
"""

import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI, FIGURE_SIZES, GRID_CONFIG, save_chart, setup_font
from hip4_hrc_palette import BODY, HYPERLIQUID, NOTE, OUTCOME, TITLE

BASE = HYPERLIQUID  # 평시
WORLD_CUP = OUTCOME  # 월드컵 기간
WC_START, WC_END = pd.Timestamp('2026-06-11'), pd.Timestamp('2026-07-19')
SPLIT = pd.Timestamp('2026-08-29')

df = pd.read_csv('outputs/data/hip4_daily_volume_since_launch.csv',
                 parse_dates=['date'])
df['musd'] = df['volume_usd'] / 1e6

setup_font()
fig, ax = plt.subplots(figsize=FIGURE_SIZES['bar'], dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 일별 바는 vlines로 (bar는 픽셀 반올림으로 폭이 들쭉날쭉해진다)
wc = df['date'].between(WC_START, WC_END)
for mask, color in ((~wc, BASE), (wc, WORLD_CUP)):
    ax.vlines(df.loc[mask, 'date'], 0, df.loc[mask, 'musd'],
              color=color, linewidth=4.2, zorder=3)

ax.set_ylim(0, 15.0)
ax.yaxis.set_major_locator(mticker.FixedLocator([0, 3, 6, 9, 12]))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
            df['date'].max() + pd.Timedelta(days=2))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# 월드컵 구간 라벨
ax.text(WC_START + pd.Timedelta(days=6), 14.7,
        'World Cup\nJun 11 To Jul 19', color=WORLD_CUP, fontsize=13,
        fontweight='bold', ha='center', va='top', linespacing=1.6)

# 8/29 퍼미션리스 배포 개시
ax.axvline(SPLIT, color=NOTE, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
ax.text(SPLIT - pd.Timedelta(days=2), 12.7,
        'Aug 29\nPermissionless\nDeployment Opens',
        color=NOTE, fontsize=12, fontweight='bold',
        ha='right', va='top', linespacing=1.6)

ANNOTATIONS = [
    ('2026-06-27', 'Jun 27 Peak, $12.05M\nSports 91%', 26, 12.7),
    ('2026-07-19', 'Jul 19 Final, $5.52M\nSports 89%', 12, 8.2),
]
for dd, label, offset_days, y in ANNOTATIONS:
    d = pd.Timestamp(dd)
    v = df.loc[df['date'] == d, 'musd'].iloc[0]
    ax.annotate(label, xy=(d, v), xytext=(d + pd.Timedelta(days=offset_days), y),
                color=TITLE, fontsize=12, fontweight='bold',
                ha='left', va='top', linespacing=1.6,
                arrowprops=dict(arrowstyle='-', color=NOTE,
                                linewidth=1, shrinkA=6, shrinkB=2))

ax.grid(axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=15, pad=12, length=0, colors=BODY)
ax.tick_params(axis='x', labelsize=14, pad=10, length=6, width=1, colors=BODY)
for lbl in ax.get_xticklabels():
    lbl.set_rotation(45)
    lbl.set_ha('right')
    lbl.set_rotation_mode('anchor')

fig.tight_layout()
png, svg = save_chart(fig, 'hip4_daily_volume_since_launch_hrc',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
