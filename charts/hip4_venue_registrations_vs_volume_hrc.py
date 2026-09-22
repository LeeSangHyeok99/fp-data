"""
HIP-4 Two Venues: Markets Registered vs Lifetime Volume, HRC dark theme.
데이터/구성은 charts/hip4_venue_registrations_vs_volume.py와 동일, 팔레트만 HRC.
"""

import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI, FIGURE_SIZES, save_chart, setup_font
from hip4_hrc_palette import BODY, OUTCOME, SKEW, TITLE

# SUIT은 Bold만 등록되어 있어 weight로는 굵기가 안 빠진다
TITLE_FONT = fm.FontProperties(
    fname='assets/font/SUIT/SUIT-ttf/SUIT-Medium.ttf', size=15)

COLOR = {'Outcome': OUTCOME, 'Skew': SKEW}

df = pd.read_csv('outputs/data/hip4_venue_registrations_vs_volume.csv')


def fmt_usd(v):
    return f'${v / 1e6:.2f}M' if v >= 1e6 else f'${v / 1e3:.2f}K'


PANELS = [
    ('Markets Registered, Aug 29 To Sep 1', 'markets_registered', str),
    ('Venue Volume, Lifetime', 'lifetime_volume_usd', fmt_usd),
]

setup_font()
fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES['bar'], dpi=DPI)
fig.patch.set_alpha(0)

for ax, (header, col, fmt) in zip(axes, PANELS):
    ax.set_facecolor('none')
    vals = df[col].values
    top = vals.max()

    ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.set_ylim(0, top * 1.32)
    ax.set_xticks(range(len(vals)), df['venue'])

    ax.bar(range(len(vals)), vals, width=0.46,
           color=[COLOR[n] for n in df['venue']], zorder=3)

    for x, v in enumerate(vals):
        ax.text(x, v + top * 0.035, fmt(v), ha='center', va='bottom',
                color=TITLE, fontsize=19, fontweight='bold')

    ax.set_title(header, color=TITLE, fontproperties=TITLE_FONT, pad=18)

    # 바닥선만 남기고 축을 지운다
    ax.axhline(0, color=BODY, linewidth=1.6, zorder=4)
    ax.set_yticks([])
    ax.tick_params(axis='x', length=0, pad=12, labelsize=17, colors=BODY)
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.subplots_adjust(wspace=0.28)
fig.tight_layout()
png, svg = save_chart(fig, 'hip4_venue_registrations_vs_volume_hrc',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
