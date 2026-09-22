"""ch6 e62: share of the visible 20-level book resting inside 10 and 25 bps.

The 10 bps share is the finding, so it takes the point colour; the 25 bps
share saturates and stays on the grey ladder as the ceiling.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, FILL, base_axes, save, setup_font)

Q2_START = datetime(2026, 4, 1)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e62_depth_migration_data.csv', parse_dates=['date'])
    d10 = df['depth_share_10'] * 100
    d25 = df['depth_share_25'] * 100

    fig, ax = plt.subplots(figsize=(12.6, 5.8), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    ax.axvspan(Q2_START, df['date'].iloc[-1], color=TITLE, alpha=0.045,
               zorder=0, linewidth=0)
    ax.text(Q2_START, 104, '  Q2 Reporting Period', fontsize=11, color=NOTE,
            ha='left', va='top', zorder=2)

    ax.fill_between(df['date'], d10, d25, color=FILL, alpha=0.13,
                    linewidth=0, zorder=1)
    ax.plot(df['date'], d25, color=BODY, linewidth=1.6, zorder=4)
    ax.plot(df['date'], d10, color=POINT, linewidth=2.2, zorder=5)

    ax.text(df['date'].iloc[-1], d25.iloc[-1] + 2.5, f'  {d25.iloc[-1]:.1f}%',
            fontsize=12, color=BODY, ha='left', va='center', zorder=6)
    ax.text(df['date'].iloc[-1], d10.iloc[-1] - 2.5, f'  {d10.iloc[-1]:.1f}%',
            fontsize=12, color=POINT, ha='left', va='center', zorder=6)

    lbl_x = datetime(2026, 3, 8)
    ax.text(lbl_x, 30, 'Within 10 bps Of Mid', fontsize=12, color=POINT,
            va='center', zorder=6)
    ax.text(lbl_x, 24, 'Within 25 bps Of Mid', fontsize=12, color=BODY,
            va='center', zorder=6)
    ax.text(lbl_x, 18, 'Share Of Visible 20-Level Depth', fontsize=12,
            color=NOTE, va='center', zorder=6)

    ax.set_ylim(0, 108)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1])
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e62_depth_migration')
