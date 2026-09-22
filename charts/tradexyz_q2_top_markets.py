"""Trade[XYZ] top 12 markets by Q2 2026 notional volume, with the QoQ delta.

Colours follow the asset-class chart so the two read as one set, with the
memory complex (MU / SNDK / SKHX) split out in red the way the book does:
it is the cohort that displaced MAG7 in the quarter.

Volume is per-market 1d candleSnapshot (v * typical price), the same series
the asset-class chart uses.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT  # noqa: E402
from tradexyz_ch7_palette import VIOLET, RED, base_axes, setup_font  # noqa: E402
from tradexyz_q2_volume_by_asset_class import SRC, OUT_DIR, save  # noqa: E402

OUT_CSV = 'outputs/data/tradexyz_q2_top_markets.csv'
Q1, Q2 = ('2026-01-01', '2026-03-31'), ('2026-04-01', '2026-06-30')
TOP = 12

INDEX_BLUE, EQUITY_NAVY = '#6E9BE8', '#2C4471'
COHORT = {
    'CL': POINT, 'BRENTOIL': POINT, 'SILVER': POINT, 'GOLD': POINT,
    'XYZ100': INDEX_BLUE, 'SP500': INDEX_BLUE,
    'SPCX': VIOLET,
    'MU': RED, 'SNDK': RED, 'SKHX': RED,          # the memory complex
}


def load():
    d = pd.read_csv(SRC)
    q = {k: d[d.date.between(*rng)].groupby('coin').notional_usd.sum() / 1e9
         for k, rng in (('q1', Q1), ('q2', Q2))}
    t = pd.DataFrame(q).fillna(0).nlargest(TOP, 'q2')
    t['qoq'] = (t.q2 / t.q1 - 1) * 100
    return t


def label(row):
    if row.q1 == 0:
        return f'${row.q2:.1f}B  (New In Q2)'
    return f'${row.q2:.1f}B  ({row.qoq:+,.0f}% QoQ)'


def draw_chart(t):
    setup_font()
    fig, ax = plt.subplots(figsize=(10.9, 5.0), dpi=150)
    fig.patch.set_alpha(0)
    base_axes(ax, axis='x')

    y = range(len(t))[::-1]
    ax.barh(y, t.q2, height=0.62, zorder=3, linewidth=0,
            color=[COHORT.get(c, EQUITY_NAVY) for c in t.index])

    for yi, (_, row) in zip(y, t.iterrows()):
        ax.text(row.q2 + 0.9, yi, label(row), fontsize=11, color=BODY,
                va='center', ha='left', zorder=4)

    ax.set_yticks(list(y))
    ax.set_yticklabels(t.index, fontsize=12, color=TITLE)
    ax.set_ylim(-0.7, len(t) - 0.3)
    ax.tick_params(axis='y', pad=6)

    ax.set_xlim(0, 58)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_xticklabels([f'${v}B' for v in (0, 10, 20, 30, 40, 50)])
    ax.tick_params(axis='x', labelsize=12, pad=5, length=5, width=1,
                   color=NOTE)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    t = load()
    t.round(4).to_csv(OUT_CSV, index_label='coin')
    print(t.round(1).to_string())
    save(draw_chart(t), 'q2_top_markets')
