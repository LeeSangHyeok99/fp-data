"""Trade[XYZ] Q2 2026 daily notional volume, split by asset class.

Commodities carry the quarter, so they take the point colour; the rest keep the
reference hues (index blue, equity navy, pre-IPO violet, ETF green, FX red)
brightened for the dark ground.

Volume is per-market 1d candleSnapshot (v * typical price), which reproduces the
S3 by_dex/xyz daily totals within 0.2%. Pre-IPO markets convert to Equities on
their listing date, the way the book treats them.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT, EVENT_LINE  # noqa: E402
from tradexyz_ch7_palette import VIOLET, RED, base_axes, setup_font  # noqa: E402

SRC = 'outputs/data/xyz_daily_volume_by_coin.csv'
OUT_CSV = 'outputs/data/tradexyz_q2_volume_by_asset_class.csv'
OUT_DIR = 'outputs/charts/tradexyz/volume'
Q2 = ('2026-04-01', '2026-06-30')

CLASSES = {
    'Commodities': 'CL BRENTOIL GOLD SILVER COPPER NATGAS PLATINUM PALLADIUM '
                   'ALUMINIUM URANIUM CORN WHEAT TTF',
    'Equity Indices': 'XYZ100 SP500 JP225 KR200 NIFTY IBOV VIX',
    'Pre-IPO & Specials': 'SPCX CBRS QNT ZHIPU MINIMAX UNITREE CXMT GIGADEV '
                          'SHEIN KSTR SHAZ DRAM PURRDAT BOT BIRD H100 LYTE '
                          'NCLD VOL',
    'ETFs': 'EWY EWJ EWT EWZ XLE SMH URNM SOXL MAGS XBI KORU',
    'FX': 'JPY EUR GBP KRW DXY',
}
# everything unmapped is a single-name equity
COIN_CLASS = {t: k for k, v in CLASSES.items() for t in v.split()}

# the perp stops being a pre-IPO market the day the stock lists
IPO_DATES = {'CBRS': '2026-05-14', 'SPCX': '2026-06-12'}

ORDER = ['Commodities', 'Equity Indices', 'Equities',
         'Pre-IPO & Specials', 'ETFs', 'FX']
COLORS = {
    'Commodities': POINT,
    'Equity Indices': '#6E9BE8',
    'Equities': '#2C4471',
    'Pre-IPO & Specials': VIOLET,
    'ETFs': '#2FB894',
    'FX': RED,
}

# (date, day label, what, label row, label x-shift in days) - the second row
# and the shift keep Jun 12 clear of Jun 15
EVENTS = [
    ('2026-04-08', 'Apr 8', 'Ceasefire', 0, 0),
    ('2026-05-14', 'May 14', 'CBRS IPO', 0, 0),
    ('2026-06-05', 'Jun 5', 'Jobs', 0, 0),
    ('2026-06-12', 'Jun 12', 'SPCX IPO', 1, -3),
    ('2026-06-15', 'Jun 15', 'Ceasefire', 0, 0),
    ('2026-06-23', 'Jun 23', 'OI Peak', 1, 0),
]


def load():
    df = pd.read_csv(SRC)
    df = df[df.date.between(*Q2)].copy()
    df['cls'] = df.coin.map(COIN_CLASS).fillna('Equities')
    listed = [df.coin.eq(t) & df.date.ge(d) for t, d in IPO_DATES.items()]
    df.loc[pd.concat(listed, axis=1).any(axis=1), 'cls'] = 'Equities'
    p = (df.pivot_table(index='date', columns='cls', values='notional_usd',
                        aggfunc='sum')
           .reindex(columns=ORDER).fillna(0) / 1e9)
    p.index = pd.to_datetime(p.index)
    return p.asfreq('D').fillna(0)


def draw_chart(p):
    setup_font()
    # sized so the saved svg lands at ~775x354 pt, the size it is placed at:
    # scaling the file down afterwards closes the gaps between the daily bars
    fig, ax = plt.subplots(figsize=(10.9, 5.0), dpi=150)
    fig.patch.set_alpha(0)
    base_axes(ax)

    bottom = pd.Series(0.0, index=p.index)
    bars = []
    for cls in ORDER:
        bars.append(ax.vlines(p.index, bottom, bottom + p[cls],
                              color=COLORS[cls], zorder=3))
        bottom += p[cls]

    top = 6.4
    for date, day, what, row, shift in EVENTS:
        x = pd.Timestamp(date)
        label_y = top - 0.62 - 0.85 * row
        ax.vlines(x, 0, label_y - 0.13, color=NOTE, **EVENT_LINE)
        ax.text(x + pd.Timedelta(days=shift), label_y, f'{day}\n{what}',
                fontsize=10, color=BODY,
                ha='center', va='bottom', linespacing=1.35, zorder=6)

    ax.set_ylim(0, top)
    ax.set_yticks([0, 2, 4, 6])
    ax.set_yticklabels(['$0B', '$2B', '$4B', '$6B'])
    ax.tick_params(axis='y', labelsize=13, pad=6)
    ax.set_xlim(p.index[0] - pd.Timedelta(days=1),
                p.index[-1] + pd.Timedelta(days=1))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=12, pad=5, length=5, width=1,
                   color=NOTE)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    fig.tight_layout()

    # bar width follows the day pitch, so the gaps survive at the placed size
    pitch = ax.get_window_extent().width / len(p) * 72 / fig.dpi
    for b in bars:
        b.set_linewidth(pitch * 0.6)
    return fig


def save(fig, name):
    from pathlib import Path
    d = Path(OUT_DIR)
    d.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(d / f'{name}.{ext}', dpi=150, facecolor='none',
                    edgecolor='none', transparent=True, bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(d / f'_preview_{name}.png', dpi=150, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', d / f'{name}.png')


if __name__ == '__main__':
    p = load()
    p.round(6).to_csv(OUT_CSV, index_label='date')
    assert abs(p.sum().sum() - 202.4) < 3, p.sum().sum()   # book prints $202.4B
    print(p.sum().round(1).to_string(), '\ntotal %.1fB' % p.sum().sum())
    save(draw_chart(p), 'q2_volume_by_asset_class')


def draw_legend(cols):
    """Standalone legend swatches, transparent, for pasting beside the chart.

    Drawn in point coordinates so the swatch and text sizes match the chart.
    """
    from matplotlib.patches import Rectangle
    setup_font()
    size, gap, col_w, row_h = 10, 6, 132, 22          # points
    rows = -(-len(ORDER) // cols)
    w, h = col_w * cols, row_h * rows
    fig = plt.figure(figsize=(w / 72, h / 72), dpi=150)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')

    for i, cls in enumerate(ORDER):
        x = col_w * (i // rows)
        y = h - row_h * (i % rows) - row_h / 2
        ax.add_patch(Rectangle((x, y - size / 2), size, size,
                               color=COLORS[cls], linewidth=0))
        ax.text(x + size + gap, y, cls, fontsize=11, color=TITLE,
                va='center', ha='left')
    return fig


if __name__ == '__main__':
    for cols in (2, 3, 6):
        save(draw_legend(cols), f'q2_volume_legend_{cols}col')
