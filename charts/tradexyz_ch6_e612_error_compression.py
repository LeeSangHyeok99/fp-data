"""ch6 e612: median absolute error against the reopening print, Q1 against Q2.

Q2 is the measured series and takes the point colour; the published Q1 figures
sit behind it as the dashed grey reference.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, base_axes, save, setup_font)

LABELS = ['Friday\nClose', 'T-24h', 'T-6h', 'Final\nPre-Open']


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e612_error_compression_data.csv')
    x = range(len(df))

    fig, ax = plt.subplots(figsize=(11.6, 5.8), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    ax.plot(x, df['q1_published_bps'], color=BODY, linewidth=2.0,
            linestyle=(0, (6, 4)), marker='o', markersize=10, zorder=3)
    ax.plot(x, df['q2_measured_bps'], color=POINT, linewidth=2.6, marker='o',
            markersize=10, zorder=4)

    for i, r in df.iterrows():
        # whichever series is on top gets the label above, so the last
        # checkpoint (where they cross) does not stack two labels on one dot
        up, down = ((POINT, 'q2_measured_bps'), (BODY, 'q1_published_bps'))
        if r['q1_published_bps'] > r['q2_measured_bps']:
            up, down = down, up
        ax.text(i, r[up[1]] + 8, f"{r[up[1]]:.0f}", fontsize=13, color=up[0],
                ha='center', va='bottom', zorder=5)
        ax.text(i, r[down[1]] - 8, f"{r[down[1]]:.0f}", fontsize=13,
                color=down[0], ha='center', va='top', zorder=5)

    ax.text(0, 218, 'Q2 2026', fontsize=13, color=POINT, ha='left',
            va='center', zorder=5)
    ax.text(0.55, 218, 'Q1 2026 (Published)', fontsize=13, color=BODY,
            ha='left', va='center', zorder=5)
    ax.text(3.15, 218, 'Median Absolute Error vs The Reopening Print (bps)',
            fontsize=12, color=NOTE, ha='right', va='center', zorder=5)
    ax.text(1.5, 22, 'Q2 Opens Each Weekend +47% Wider Than Q1 And Still '
            'Closes 16% Tighter.', fontsize=12, color=NOTE, ha='center',
            va='center', zorder=5)

    ax.set_ylim(0, 232)
    ax.set_yticks([0, 50, 100, 150, 200])
    ax.set_xlim(-0.35, 3.35)
    ax.set_xticks(list(x))
    ax.set_xticklabels(LABELS, fontsize=13)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e612_error_compression')
