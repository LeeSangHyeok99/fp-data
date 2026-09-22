"""ch6 e613: hit rate by the size of the weekend gap the traditional venue printed.

Below 25 bps the pre-open mark loses to Friday's close, so that bucket goes
red; the published Q1 rate sits over each bar as a dashed marker.
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, RED, base_axes, save, setup_font)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e613_hit_by_gap_data.csv')
    hit = df['hit'] * 100
    colors = [RED if h < 50 else POINT for h in hit]

    fig, ax = plt.subplots(figsize=(11.6, 5.8), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    x = range(len(df))
    # solid at the top, fading down into the background
    for i, (h, c) in enumerate(zip(hit, colors)):
        grad = np.ones((256, 1, 4))
        grad[:, :, :3] = to_rgb(c)
        grad[:, :, 3] = np.linspace(1.0, 0.45, 256).reshape(-1, 1)
        ax.imshow(grad, extent=(i - 0.31, i + 0.31, 0, h), origin='upper',
                  aspect='auto', interpolation='bilinear', zorder=3)
    ax.axhline(50, color=BODY, linewidth=1.2, zorder=4)

    for i, r in df.iterrows():
        c = colors[i]
        # clear the Q1 marker when it sits above the bar top
        top = max(hit[i], r['q1'] * 100 if r['q1'] * 100 > hit[i] else 0)
        ax.text(i, top + 2, f'{hit[i]:.0f}%', fontsize=15, color=c,
                ha='center', va='bottom', zorder=5)
        ax.plot([i - 0.31, i + 0.31], [r['q1'] * 100] * 2, color=BODY,
                linewidth=2.4, linestyle=(0, (4, 3)), zorder=5)
        ax.text(i, 4, f"N={int(r['n'])}\n{r['improvement']:+.0f} bps",
                fontsize=12, color=c, ha='center', va='bottom', zorder=6)

    ax.text(-0.42, 126, 'Share Of Weekends The Pre-Open Mark Beat Friday\'s '
            'Close', fontsize=12, color=NOTE, ha='left', va='center', zorder=5)
    ax.text(-0.42, 112, 'Q2 2026', fontsize=13, color=POINT, ha='left',
            va='center', zorder=5)
    ax.text(0.18, 112, 'Q1 2026 (Published)', fontsize=13, color=BODY,
            ha='left', va='center', zorder=5)
    ax.text(1.40, 112, 'Perp Loses To Friday\'s Close', fontsize=13,
            color=RED, ha='left', va='center', zorder=5)

    ax.set_ylim(0, 134)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlim(-0.55, 3.55)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f'{b} bps' for b in df['bucket']], fontsize=13)
    ax.set_xlabel('Size Of The Weekend Gap The Traditional Venue Actually '
                  'Printed', fontsize=12, color=NOTE, labelpad=10)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e613_hit_by_gap')
