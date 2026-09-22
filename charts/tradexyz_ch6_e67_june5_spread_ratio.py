"""ch6 e67: June 5 hourly spread against the same hour on five weekdays.

Two separate exports: the per-contract panel (top) and the cohort baseline
panel (bottom), which is the actual argument.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, DIM, COHORT_COLORS, base_axes, save,
    setup_font)

ORDER = ['Korean listings', 'US semiconductors', 'Index reference']
# the Thursday-only baseline is not in the CSV; recovered from the reference
# export's marker positions (tradeXYZ_Inforgraphic_retouch/ch6/*.svg, linear
# x-scale solved against the two baselines that are in the CSV)
# ponytail: hard-coded, move into the CSV if the hourly source is rebuilt
THU_ONLY = {'Korean listings': 1.115, 'US semiconductors': 0.896,
            'Index reference': 1.004}
TICKS = [0.25, 0.5, 1, 2, 4, 10, 25, 50]


def _radius(ax, size_pt):
    """Half a marker of that point size, in x and y data units."""
    inv = ax.transData.inverted()
    px = size_pt / 2 * ax.figure.dpi / 72
    x0, y0 = inv.transform((0, 0))
    return (abs(inv.transform((px, 0))[0] - x0),
            abs(inv.transform((0, px))[1] - y0))


def _pieces(lo, hi, holes):
    """lo..hi minus every (a, b) hole, as a list of segments."""
    out = [(lo, hi)]
    for a, b in holes:
        nxt = []
        for x0, x1 in out:
            if b <= x0 or a >= x1:
                nxt.append((x0, x1))
                continue
            if a > x0:
                nxt.append((x0, a))
            if b < x1:
                nxt.append((b, x1))
        out = nxt
    return out


def load():
    df = pd.read_csv(DATA / 'e67_june5_spread_ratio_data.csv')
    df['cohort_label'] = pd.Categorical(df['cohort_label'], ORDER, ordered=True)
    df = df.sort_values(['cohort_label', 'med_weekday_baseline'],
                        ascending=[True, False]).reset_index(drop=True)
    # one blank row between cohorts so the groups read apart
    rows, y, prev = [], 0, None
    for _, r in df.iterrows():
        if prev is not None and r['cohort_label'] != prev:
            y += 1
        rows.append(y)
        prev, y = r['cohort_label'], y + 1
    df['y'] = rows
    return df


def draw_top():
    setup_font()
    df = load()
    fig, ax = plt.subplots(figsize=(23.0, 9.45), dpi=DPI)
    fig.patch.set_alpha(0)

    base_axes(ax, axis='x')
    ax.tick_params(labelsize=24)
    ax.set_xscale('log')
    ax.plot([1, 1], [-0.65, df['y'].max() + 0.45], color=BODY, linewidth=1.2,
            zorder=4)
    ax.text(1, -1.58, 'Parity', fontsize=24, color=BODY, ha='center',
            va='bottom', zorder=5)

    for _, r in df.iterrows():
        c = COHORT_COLORS[r['cohort_label']]
        ax.plot([r['p25'], r['p75']], [r['y']] * 2, color=c, linewidth=9.5,
                alpha=0.35, solid_capstyle='round', zorder=3)
        ax.plot(r['med_weekday_baseline'], r['y'], 'o', color=c,
                markersize=18, zorder=5)
        ax.plot([r['peak']] * 2, [r['y'] - 0.22, r['y'] + 0.22], color=DIM,
                linewidth=2.6, zorder=4)
        ax.text(0.155, r['y'], r['sym'], fontsize=24, color=c, ha='left',
                va='center', zorder=5)
        ax.text(72, r['y'], f"{r['med_weekday_baseline']:.2f}x", fontsize=24,
                color=TITLE, ha='left', va='center', zorder=5)
        ax.text(150, r['y'], f"{r['peak']:.1f}x", fontsize=24, color=NOTE,
                ha='left', va='center', zorder=5)

    ax.text(72, -1.1, 'Median', fontsize=24, color=BODY, ha='left',
            va='center', zorder=5)
    ax.text(150, -1.1, 'Worst Hr', fontsize=24, color=NOTE, ha='left',
            va='center', zorder=5)
    ax.text(0.155, -1.1, 'Bar Is The Middle Half Of That Contract\'s Hourly '
            'Ratios.  Grey Tick Is Its Single Worst Hour.', fontsize=20,
            color=NOTE, ha='left', va='center', zorder=5)

    ax.set_xlim(0.15, 260)
    ax.set_xticks(TICKS)
    ax.set_xticklabels([f'{t:g}x' for t in TICKS])
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_ylim(df['y'].max() + 0.7, -1.9)
    ax.set_yticks([])
    ax.set_xlabel('June 5 Hourly Spread ÷ Same Hour Across The Five '
                  'Surrounding Weekdays  (Log Scale)', fontsize=24,
                  color=NOTE, labelpad=10)
    fig.tight_layout()
    return fig


def draw_bottom():
    setup_font()
    df = load()
    fig, ax = plt.subplots(figsize=(23.0, 4.73), dpi=DPI)
    fig.patch.set_alpha(0)

    base_axes(ax, axis='x')
    ax.tick_params(labelsize=24)
    # limits first: the marker radii below are read off the final transform
    ax.set_xlim(0.30, 2.3)
    ax.set_ylim(3.2, -0.6)

    rx, ry = _radius(ax, 27)
    parity_holes = []
    for i, cohort in enumerate(ORDER):
        g = df[df['cohort_label'] == cohort]
        c = COHORT_COLORS[cohort]
        five = g['med_weekday_baseline'].median()
        thu_sat = g['med_thu_sat_baseline'].median()
        thu = THU_ONLY[cohort]
        # the open markers are hollow, so neither the connector nor the parity
        # rule may run under one
        pts = sorted((five, thu, thu_sat))
        for a, b in zip(pts, pts[1:]):
            if b - a > 2 * rx:
                ax.plot([a + rx, b - rx], [i] * 2, color=c, linewidth=3.0,
                        alpha=0.55, zorder=3)
        for xm in (thu, thu_sat):
            if abs(xm - 1) < rx:
                parity_holes.append((i - ry, i + ry))
        ax.plot(five, i, 'o', color=c, markersize=26, zorder=5)
        ax.plot(thu, i, 'o', color='none', markeredgecolor=c,
                markeredgewidth=3.8, markersize=26, zorder=5)
        ax.plot(thu_sat, i, 's', color='none', markeredgecolor=c,
                markeredgewidth=4.1, markersize=27, zorder=5)
        ax.text(five, i - 0.30, f'{five:.2f}x', fontsize=24, color=TITLE,
                ha='center', va='bottom', zorder=5)
        # a square sitting on top of the other markers has no room to label
        if abs(thu_sat - five) > 0.15:
            ax.annotate(f'{thu_sat:.2f}x', (thu_sat, i), xytext=(32, 0),
                        textcoords='offset points', fontsize=24, color=c,
                        ha='left', va='center', zorder=5)
        ax.text(0.315, i, cohort.title().replace('Us ', 'US '), fontsize=24,
                color=c, ha='left', va='center', zorder=5)

    for lo, hi in _pieces(-0.45, 2.45, parity_holes):
        ax.plot([1, 1], [lo, hi], color=BODY, linewidth=1.2, zorder=4)

    ax.set_xticks([0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2])
    ax.set_xticklabels(['0.6x', '0.8x', '1x', '1.2x', '1.4x', '1.6x', '1.8x',
                        '2x', '2.2x'])
    ax.set_yticks([])
    ax.set_xlabel('Cohort Typical Ratio, Median Of The Contract Medians',
                  fontsize=24, color=NOTE, labelpad=10)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_top(), 'e67_june5_spread_ratio_top')
    save(draw_bottom(), 'e67_june5_spread_ratio_bottom')
