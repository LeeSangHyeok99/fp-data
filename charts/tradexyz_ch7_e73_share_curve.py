"""ch7 e73: daily Trade[XYZ] share of HIP-3 volume against both denominators.

The all-namespace denominator is the headline number, so it takes the point
colour; the Q1-peer-set-only denominator rides underneath in grey to show the
two never separate by much. Red rules mark the wind-down dates.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch7_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, FILL, RED, base_axes, save,
    setup_font)

# the four settlement dates the curve is meant to be read against
EVENTS = [
    (datetime(2026, 6, 18), 'km Delisted Jun 18', 83.0),
    (datetime(2026, 6, 20), 'Ventuals Settled Jun 20', 77.5),
    (datetime(2026, 6, 21), 'Felix Settled Jun 21', 72.0),
    (datetime(2026, 6, 30), 'Dreamcash Begins Settling Jun 30', 66.5),
]
LABEL_ANCHOR = datetime(2026, 6, 16)  # all four labels hang off one edge


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e73_share_curve_data.csv', parse_dates=['date'])
    all_ns = df['xyz_share_all'] * 100
    peers = df['xyz_share_q1peers'] * 100

    fig, ax = plt.subplots(figsize=(13.0, 6.0), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    ax.axhline(95, color=BODY, linewidth=1.2, linestyle=(0, (5, 4)), zorder=3)
    ax.text(datetime(2026, 3, 26), 95.6, '95%', fontsize=12, color=BODY,
            ha='left', va='bottom', zorder=4)

    for d, label, y in EVENTS:
        ax.axvline(d, color=RED, linewidth=1.2, alpha=0.55,
                   linestyle=(0, (5, 4)), zorder=2)
        ax.text(LABEL_ANCHOR, y, f'{label}  ', fontsize=11.5, color=RED,
                ha='right', va='center', zorder=5)

    ax.plot(df['date'], peers, color=FILL, linewidth=2.6, alpha=0.55, zorder=4)
    ax.plot(df['date'], all_ns, color=POINT, linewidth=1.8, zorder=5)

    last = df['date'].iloc[-1]
    # marker sits on the last date, so let it spill past the axes edge
    ax.plot(last, all_ns.iloc[-1], 'o', color=POINT, markersize=8, zorder=6,
            clip_on=False)
    ax.text(last, all_ns.iloc[-1] + 1.4, f'{all_ns.iloc[-1]:.1f}%',
            fontsize=14, color=TITLE, ha='right', va='bottom', zorder=6)

    lbl_x = datetime(2026, 3, 14)
    ax.text(lbl_x, 66.0, 'Vs All Deployer Namespaces', fontsize=12.5,
            color=POINT, va='center', zorder=6)
    ax.text(lbl_x, 62.5, 'Vs The Q1 Peer Set Only', fontsize=12.5, color=FILL,
            va='center', zorder=6)
    ax.text(lbl_x, 59.0, 'The Two Denominators Never Diverge By More Than '
            '6.6pp', fontsize=12, color=NOTE, va='center', zorder=6)

    ax.set_ylim(56.5, 103)
    ax.set_yticks([60, 70, 80, 90, 100])
    ax.set_yticklabels(['60%', '70%', '80%', '90%', '100%'])
    ax.set_xlim(df['date'].iloc[0], last)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', length=5, width=1.1, color=NOTE, pad=5)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e73_share_curve')
