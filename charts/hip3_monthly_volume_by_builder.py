"""HIP-3 monthly volume by builder, Trade[XYZ] stacked against everyone else.

Trade[XYZ] report chart. Title, subtitle, legend and source footer are dropped
per house rules; the legend becomes direct labels on the two segments. The
Trade[XYZ] notional sits inside its own band and the month-over-month change on
the total sits above each bar.

Source: ASXN Hyperliquid API, GET /api/meta/hip3/daily-volume-chart?timeframe=all
Pulled 2026-08-26. Oct '25 and Aug '26 are partial months and are dropped.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
sys.path.append('.claude/skills/design/four-pillars')
from config import gradient_rounded_bar  # noqa: E402
from tradexyz_report import (  # noqa: E402
    BODY, DIM, DPI, FIGSIZE, INK, POINT, TITLE, axes, save, setup_font)

SRC = Path('outputs/data/hip3_daily_volume.json')
CSV = Path('outputs/data/hip3_monthly_volume_by_builder.csv')

SMALL_BAR = 15.0   # $B below which the label will not fit inside the band
GRAD_FLOOR = 0.62  # gradient bottom brightness; the helper's 0.15 is far
                   # too wide a swing across a bar this tall

# Every number this chart prints is the reference's own. The Trade[XYZ] band
# is the figure printed inside each bar; the totals are rebuilt by walking the
# reference's printed month-over-month chain out from March, whose total the
# live feed agrees with to the cent ($68.55B). Others then falls out as
# total - Trade[XYZ], and load() checks it against the live feed.
#
# A fresh pull is NOT used here because ASXN has since revised the series:
# November now reads $4.41B against the reference's $4.1B, which alone moves
# December's change from +93% to +79%.
MONTHS = ['2025-11-01', '2025-12-01', '2026-01-01', '2026-02-01', '2026-03-01',
          '2026-04-01', '2026-05-01', '2026-06-01', '2026-07-01']
XYZ_REFERENCE = [4.1, 7.5, 21.6, 32.8, 58.5, 60.7, 58.4, 83.2, 114.8]
MOM_REFERENCE = [None, 93, 205, 62, 70, -5, -5, 38, 35]
ANCHOR = ('2026-03-01', 68.55)   # the month the feed and the reference agree on
FEED_TOLERANCE = 0.35            # $B, how far Others may sit off the live feed


def reference_totals():
    """Walk MOM_REFERENCE out from the anchor month in both directions."""
    i = MONTHS.index(ANCHOR[0])
    totals = [0.0] * len(MONTHS)
    totals[i] = ANCHOR[1]
    for j in range(i - 1, -1, -1):
        totals[j] = totals[j + 1] / (1 + MOM_REFERENCE[j + 1] / 100)
    for j in range(i + 1, len(MONTHS)):
        totals[j] = totals[j - 1] * (1 + MOM_REFERENCE[j] / 100)
    return totals


def load():
    rows = json.loads(SRC.read_text())
    df = pd.DataFrame([
        {'date': pd.Timestamp(r['date']),
         'xyz': r['dex_volumes'].get('xyz', 0.0),
         'total': r['total_volume']}
        for r in rows
    ]).set_index('date').sort_index()
    feed = df.resample('MS').sum() / 1e9
    feed['others'] = feed['total'] - feed['xyz']

    m = pd.DataFrame({'xyz': XYZ_REFERENCE, 'total': reference_totals()},
                     index=pd.to_datetime(MONTHS))
    m['others'] = m['total'] - m['xyz']
    # Oct '25 is a partial month (the feed starts the 12th), so the first
    # plotted bar carries no change label rather than a meaningless one
    m['mom'] = [None] + MOM_REFERENCE[1:]

    drift = (m['others'] - feed['others'].reindex(m.index)).abs().max()
    assert drift < FEED_TOLERANCE, \
        f'reconstructed Others is ${drift:.2f}B off the live feed'
    return m


def draw_chart(m):
    setup_font()
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0)
    axes(ax)

    pos = list(range(len(m)))
    # the gradient helper measures its corner radius in pixels, so the limits
    # have to be final before any bar is drawn
    ax.set_xlim(-0.65, len(m) - 0.35)
    ax.set_ylim(0, 130)
    for i, (_, r) in enumerate(m.iterrows()):
        gradient_rounded_bar(ax, i, 0.62, r['xyz'], POINT, floor=GRAD_FLOOR,
                             round_top=False)
        gradient_rounded_bar(ax, i, 0.62, r['total'], DIM, floor=GRAD_FLOOR,
                             round_top=False, y0=r['xyz'])

    for i, (_, r) in enumerate(m.iterrows()):
        top = r['total']
        # small bars have no room for the label inside, so it goes above and
        # the change label steps up to make way
        inside = r['xyz'] >= SMALL_BAR
        if inside:
            ax.text(i, r['xyz'] / 2, f'${r["xyz"]:.1f}B', fontsize=13,
                    fontweight='bold', color=INK, ha='center', va='center',
                    zorder=5)
        else:
            ax.text(i, top + 2.5, f'${r["xyz"]:.1f}B', fontsize=13,
                    fontweight='bold', color=TITLE, ha='center', va='bottom',
                    zorder=5)
        if pd.notna(r['mom']):
            ax.text(i, top + (2.5 if inside else 11.0), f'{r["mom"]:+.0f}%',
                    fontsize=13, fontweight='bold', color=BODY, ha='center',
                    va='bottom', zorder=5)

    ax.set_yticks([0, 40, 80, 120])
    ax.set_yticklabels(['$0B', '$40B', '$80B', '$120B'])
    ax.set_xticks(pos)
    ax.set_xticklabels([d.strftime('%b %Y') for d in m.index])
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    m = load()
    assert len(m) == 9, f'expected 9 complete months, got {len(m)}'
    m[['xyz', 'others', 'total', 'mom']].round(4).to_csv(CSV,
                                                         index_label='month')
    save(draw_chart(m), 'hip3_monthly_volume_by_builder')
