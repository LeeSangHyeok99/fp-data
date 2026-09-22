"""ch7 e71: first-to-last fill span for every HIP-3 deployer namespace.

Bars run from first fill to last fill. A faded left end means the deployer was
already trading when HIP-3 history begins on Feb 1, so that edge is not a
launch date; only para has a real rounded launch cap.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('charts')
from matplotlib.colors import to_rgb

from tradexyz_ch7_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, RED, NS_COLORS,
    base_axes, save, setup_font)

HISTORY_START = datetime(2026, 2, 1)
Q2_CLOSE = datetime(2026, 6, 30)
BAR_H = 0.27  # bar thickness in row units


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e71_deployer_timeline_data.csv',
                     parse_dates=['first', 'last', 'all_zero', 'announced'])

    fig, ax = plt.subplots(figsize=(13.0, 6.4), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax, grid=False)

    months = [mdates.date2num(datetime(2026, m, 1)) for m in range(2, 8)]
    ax.set_ylim(-0.85, len(df) - 0.15)
    ax.set_yticks([])
    ax.set_xlim(mdates.date2num(HISTORY_START) - 74,
                mdates.date2num(datetime(2026, 7, 26)))
    ax.set_xticks(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.vlines(months, -0.62, len(df) - 0.38, color=NOTE, alpha=0.35,
              linewidth=0.9, linestyle=(0, (3.7, 1.6)), zorder=1)

    for i, r in df.iterrows():
        y = len(df) - 1 - i
        c = NS_COLORS[r['namespace']]
        x0, x1 = mdates.date2num(r['first']), mdates.date2num(r['last'])
        grad = np.ones((1, 256, 4))
        grad[:, :, :3] = to_rgb(c)
        grad[:, :, 3] = np.linspace(0.4, 1.0, 256)
        ax.imshow(grad, extent=(x0, x1, y - BAR_H / 2, y + BAR_H / 2),
                  aspect='auto', interpolation='bilinear', zorder=3)

        ax.text(mdates.date2num(HISTORY_START) - 11, y,
                f"({int(r['markets'])} Mkts)", fontsize=12, color=NOTE,
                ha='right', va='center', zorder=6)
        ax.text(mdates.date2num(HISTORY_START) - 33, y,
                r['display_name'], fontsize=14, color=TITLE,
                ha='right', va='center', zorder=6)

        if pd.notna(r['announced']):
            ax.plot([mdates.date2num(r['announced'])] * 2,
                    [y - 0.26, y + 0.26], color=TITLE, linewidth=2.2, zorder=5)
            ax.text(mdates.date2num(r['announced']), y + 0.34, 'Announced',
                    fontsize=11, color=BODY, ha='center', va='bottom', zorder=6)

        if pd.notna(r['all_zero']) and c == RED:
            z = mdates.date2num(r['all_zero']) + 2  # clear of the bar end
            ax.plot(z, y, 'o', color='none', markeredgecolor=RED,
                    markeredgewidth=2.4, markersize=13, zorder=5)
            ax.annotate(f"Zero OI {r['all_zero'].strftime('%b %-d')}", (z, y),
                        xytext=(14, 0), textcoords='offset points',
                        fontsize=12, color=RED, ha='left', va='center',
                        zorder=6)

    ax.set_ylim(-0.85, len(df) - 0.15)
    ax.set_xlim(mdates.date2num(HISTORY_START) - 74,
                mdates.date2num(datetime(2026, 7, 26)))

    ax.axvline(mdates.date2num(Q2_CLOSE), color=NOTE, linewidth=1.3,
               linestyle=(0, (5, 4)), zorder=2)
    ax.text(mdates.date2num(Q2_CLOSE) - 3, len(df) - 0.35, 'Q2 Close',
            fontsize=12, color=NOTE, ha='right', va='center', zorder=6)

    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e71_deployer_timeline')
