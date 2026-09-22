"""Trade[XYZ] index complex: SP500 monthly notional against the XYZ100 baseline.

SP500 is what the chart is about, so it takes the point colour; XYZ100 stays
on the index blue the rest of the set uses for that cohort.

Monthly sums of the per-market daily series (Hyperliquid public API,
candleSnapshot on the xyz dex).
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import BODY, NOTE, POINT  # noqa: E402
from tradexyz_ch7_palette import base_axes, setup_font  # noqa: E402
from tradexyz_q2_volume_by_asset_class import SRC, save  # noqa: E402

sys.path.append('.claude/skills/design/four-pillars')
from config import gradient_rounded_bar  # noqa: E402

OUT_DIR = 'outputs/charts/tradexyz/volume'
OUT_CSV = 'outputs/data/tradexyz_index_complex_monthly.csv'
H1 = ('2026-01-01', '2026-06-30')

BLUE = '#6E9BE8'
SERIES = [('XYZ100', BLUE, 'XYZ100 (Nasdaq-Style)'),
          ('SP500', POINT, 'SP500 (Licensed, Live Mar 18)')]


def load():
    d = pd.read_csv(SRC, parse_dates=['date'])
    d = d[d.coin.isin([s[0] for s in SERIES]) & d.date.between(*H1)]
    m = (d.groupby([d.date.dt.strftime('%b %Y'), 'coin']).notional_usd.sum()
         / 1e9).unstack()
    return m.reindex(pd.date_range(*H1, freq='MS').strftime('%b %Y'))


def draw_chart(m):
    setup_font()
    fig, ax = plt.subplots(figsize=(10.9, 4.6), dpi=150)
    fig.patch.set_alpha(0)
    base_axes(ax)

    x = np.arange(len(m))
    w, gap = 0.36, 0.09

    # limits first: the gradient fill measures its corner radius in pixels
    ax.set_ylim(0, 16)
    ax.set_yticks([0, 5, 10, 15])
    ax.set_yticklabels(['$0B', '$5B', '$10B', '$15B'])
    ax.tick_params(axis='y', labelsize=13, pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels(m.index, fontsize=12, color=NOTE)
    ax.set_xlim(-0.65, len(m) - 0.35)
    ax.tick_params(axis='x', pad=5, length=5, width=1, color=NOTE)
    ax.set_autoscale_on(False)

    for i, (coin, color, _) in enumerate(SERIES):
        off = (i - 0.5) * (w + gap)
        for xi, val in zip(x + off, m[coin]):
            if pd.isna(val):
                continue
            # floor high, round_top off: a flat bar with a shallow gradient
            gradient_rounded_bar(ax, xi, w, val, color, floor=0.62,
                                 round_top=False)
            ax.text(xi, val + 0.3, f'{val:.1f}', fontsize=11, color=color,
                    ha='center', va='bottom', zorder=4)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    import tradexyz_q2_volume_by_asset_class as base
    base.OUT_DIR = OUT_DIR
    m = load()
    m.round(4).to_csv(OUT_CSV)
    print(m.round(2).to_string())
    save(draw_chart(m), 'index_complex_monthly')
