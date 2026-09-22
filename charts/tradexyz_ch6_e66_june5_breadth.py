"""ch6 e66: every Trade[XYZ] market's June 5 return, sorted.

Memory and semiconductor names led the selloff, so they take the point colour
and everything else drops to the dim grey.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, BODY, NOTE, POINT, DIM, base_axes, save, setup_font)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e66_june5_breadth_data.csv')
    df = df.sort_values('ret_pct', ascending=False).reset_index(drop=True)
    df['label'] = df['coin'].str.replace('xyz:', '', regex=False)
    colors = [POINT if s else DIM for s in df['is_semi']]

    fig, ax = plt.subplots(figsize=(26.0, 13.0), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax, axis='x')

    y = range(len(df))
    ax.barh(y, df['ret_pct'], color=colors, height=0.72, zorder=3)
    ax.axvline(0, color=BODY, linewidth=1.0, zorder=4)

    ax.set_yticks(list(y))
    ax.set_yticklabels(df['label'], fontsize=11)
    ax.invert_yaxis()
    ax.set_ylim(len(df) - 0.4, -0.6)

    for i in df.index[-5:]:
        ax.text(df.loc[i, 'ret_pct'] - 0.25, i, f"{df.loc[i, 'ret_pct']:.1f}%",
                fontsize=11, color=POINT, ha='right', va='center', zorder=5)

    ax.text(-16.5, 3.0, '56 Of 68 Markets Fell More Than 2%.\n'
            '0 Rose More Than 2%.', fontsize=15, color=BODY, ha='left',
            va='top', zorder=5)
    ax.text(-16.5, 9.5, 'Memory / Semiconductors', fontsize=12, color=POINT,
            ha='left', va='top', zorder=5)
    ax.text(-16.5, 11.2, 'All Other xyz Markets', fontsize=12, color=DIM,
            ha='left', va='top', zorder=5)
    ax.text(-16.5, 14.5, 'Daily Return, June 5 Close Against June 4 Close',
            fontsize=12, color=NOTE, ha='left', va='top', zorder=5)

    ax.set_xlim(-17.4, 1.2)
    ax.set_xticks([-15, -10, -5, 0])
    ax.set_xticklabels(['-15%', '-10%', '-5%', '0%'])

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e66_june5_breadth')
