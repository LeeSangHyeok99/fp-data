"""Trade[XYZ] weekend/weekday volume ratio by asset class, Q1 against Q2 2026.

Q2 is the quarter under discussion, so it takes the point colour and Q1 sits on
the grey ladder behind it. The venue-wide Q2 ratio runs across as a red rule.

Ratio = mean Saturday/Sunday daily notional over mean weekday notional, per
asset class, from the same per-market daily series as the rest of the set.
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import BODY, NOTE, POINT  # noqa: E402
from tradexyz_ch7_palette import DIM, RED, base_axes, setup_font  # noqa: E402
from tradexyz_q2_volume_by_asset_class import (  # noqa: E402
    SRC, COIN_CLASS, IPO_DATES, save)

sys.path.append('.claude/skills/design/four-pillars')
from config import gradient_rounded_bar  # noqa: E402

OUT_DIR = 'outputs/charts/tradexyz/volume'
OUT_CSV = 'outputs/data/tradexyz_weekend_ratio.csv'
H1 = ('2026-01-01', '2026-06-30')
CLASSES = ['Commodities', 'Equity Indices', 'Equities', 'ETFs',
           'Pre-IPO & Specials', 'FX']
QUARTERS = [('Q1', DIM), ('Q2', POINT)]

# Q1 pre-IPO volume sits in markets the current API universe no longer lists,
# so only the book's own aggregation has it. Used by the `ref` variant.
REF_PATCH = {('Pre-IPO & Specials', 'Q1'): 0.05}


def ratio(g):
    if g.empty:
        return np.nan
    day = g.groupby(['date', g.date.dt.dayofweek >= 5]).notional_usd.sum()
    wknd = day.xs(True, level=1) if True in day.index.get_level_values(1) else None
    week = day.xs(False, level=1) if False in day.index.get_level_values(1) else None
    if week is None or week.mean() == 0:
        return np.nan
    return (wknd.mean() if wknd is not None else 0.0) / week.mean()


def load(reference=False):
    d = pd.read_csv(SRC, parse_dates=['date'])
    d = d[d.date.between(*H1)].copy()
    d['cls'] = d.coin.map(COIN_CLASS).fillna('Equities')
    for ticker, listed in IPO_DATES.items():
        d.loc[(d.coin == ticker) & (d.date >= listed), 'cls'] = 'Equities'
    d['q'] = d.date.dt.quarter.map({1: 'Q1', 2: 'Q2'})

    t = pd.DataFrame(
        {q: {c: ratio(d[(d.cls == c) & (d.q == q)]) for c in CLASSES}
         for q, _ in QUARTERS})
    if reference:
        for (c, q), v in REF_PATCH.items():
            t.loc[c, q] = v
    venue = {q: ratio(d[d.q == q]) for q, _ in QUARTERS}
    return t, venue


def draw_chart(t, venue):
    setup_font()
    fig, ax = plt.subplots(figsize=(10.9, 4.6), dpi=150)
    fig.patch.set_alpha(0)
    base_axes(ax)

    x = np.arange(len(CLASSES))
    w, gap = 0.36, 0.08

    ax.axhline(venue['Q2'], color=RED, linewidth=1.2, linestyle=(0, (6, 4)),
               zorder=2)
    ax.text(2.55, 0.46, f"All XYZ, Q2 {venue['Q2']:.2f} "
            f"(Q1 {venue['Q1']:.2f})", fontsize=11, color=RED, ha='left',
            va='bottom', zorder=5)

    ax.text(-0.42, 1.10, 'Q1 2026', fontsize=12, color=DIM, ha='left',
            va='center', zorder=4)
    ax.text(-0.42, 0.99, 'Q2 2026', fontsize=12, color=POINT, ha='left',
            va='center', zorder=4)

    ax.set_ylim(0, 1.32)
    ax.set_yticks([0, 0.3, 0.6, 0.9, 1.2])
    ax.set_yticklabels(['0.0', '0.3', '0.6', '0.9', '1.2'])
    ax.tick_params(axis='y', labelsize=13, pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels(CLASSES, fontsize=12, color=NOTE)
    ax.set_xlim(-0.6, len(CLASSES) - 0.4)
    ax.tick_params(axis='x', pad=5, length=5, width=1, color=NOTE)
    ax.set_autoscale_on(False)

    # bars last: the gradient fill measures its geometry off the fixed limits
    for i, (q, color) in enumerate(QUARTERS):
        off = (i - 0.5) * (w + gap)
        for xi, val in zip(x + off, t[q]):
            if pd.isna(val):
                continue
            gradient_rounded_bar(ax, xi, w, val, color, floor=0.62,
                                 round_top=False)
            ax.text(xi, val + 0.022, f'{val:.2f}', fontsize=11, color=color,
                    ha='center', va='bottom', zorder=4)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    import tradexyz_q2_volume_by_asset_class as base
    base.OUT_DIR = OUT_DIR
    for ref in (False, True):
        t, venue = load(reference=ref)
        if not ref:
            t.round(4).to_csv(OUT_CSV, index_label='asset_class')
            print(t.round(3).to_string())
            print('All XYZ', {k: round(v, 3) for k, v in venue.items()})
        save(draw_chart(t, venue),
             'weekend_ratio_ref' if ref else 'weekend_ratio')
