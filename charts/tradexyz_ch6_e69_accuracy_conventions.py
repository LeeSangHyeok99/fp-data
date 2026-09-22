"""ch6 e69: the pre-listing mark at two checkpoints against the Nasdaq open.

One dumbbell per conversion, open circle an hour before the 13:30 UTC session
open, filled circle an hour before the opening cross.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, MARKET_COLORS, base_axes, save, setup_font)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e69_accuracy_conventions_data.csv')

    fig, ax = plt.subplots(figsize=(12.6, 5.4), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax, axis='x')

    ax.plot([0, 0], [-0.55, 2.55], color=BODY, linewidth=1.2, zorder=4)
    ax.text(0.6, -0.55, 'Realized Nasdaq Open', fontsize=12, color=BODY,
            ha='left', va='bottom', zorder=5)

    for i, r in df.iterrows():
        c = MARKET_COLORS[r['market']]
        ax.plot([r['session_pct'], r['cross_pct']], [i] * 2, color=c,
                linewidth=3.0, alpha=0.6, zorder=3)
        ax.plot(r['session_pct'], i, 'o', color='none', markeredgecolor=c,
                markeredgewidth=2.4, markersize=14, zorder=5)
        ax.plot(r['cross_pct'], i, 'o', color=c, markersize=14, zorder=5)
        ax.text(r['session_pct'], i - 0.22, f"{r['session_pct']:+.1f}%",
                fontsize=12, color=c, ha='center', va='bottom', zorder=5)
        ax.text(r['cross_pct'], i + 0.22, f"{r['cross_pct']:+.1f}%",
                fontsize=12, color=TITLE, ha='center', va='top', zorder=5)
        ax.text(-42, i, f"{r['market']}", fontsize=14, color=c, ha='left',
                va='bottom', zorder=5)
        ax.text(-42, i, f"  {r['conversion']}   Open ${r['open']:,.2f}",
                fontsize=11, color=NOTE, ha='left', va='top', zorder=5)

    ax.text(-42, 2.72, 'Open Circle Is T_session, The Hour Before The 13:30 '
            'UTC Session Open.  Filled Circle Is T_cross, The Hour Before The '
            'Opening Cross.', fontsize=11, color=NOTE, ha='left', va='center',
            zorder=5)

    ax.set_xlim(-43, 42)
    ax.set_xticks([-20, -10, 0, 10, 20, 30, 40])
    ax.set_xticklabels(['-20%', '-10%', '0%', '+10%', '+20%', '+30%', '+40%'])
    ax.set_ylim(2.85, -0.75)
    ax.set_yticks([])
    ax.set_xlabel('Pre-Listing Mark Against The Realized Nasdaq Opening Print',
                  fontsize=12, color=NOTE, labelpad=10)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e69_accuracy_conventions')
