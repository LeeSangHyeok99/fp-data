"""Trade[XYZ] venue open interest (H1) over daily liquidation notional (Q2).

OI is the story, so it takes the point colour on the upper panel; liquidations
sit underneath in red on their own scale, sharing the date axis.

OI: daily S3 snapshots (long+short notional), re-dated to the snapshot's own
day so the milestones line up with the book (first $3B close Jun 3, peak
Jun 23). Liquidations: ASXN HIP-3 API, xyz dex only, Q2 coverage.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT  # noqa: E402
from tradexyz_ch7_palette import RED, base_axes, setup_font  # noqa: E402
from tradexyz_q2_volume_by_asset_class import save  # noqa: E402

OUT_DIR = 'outputs/charts/tradexyz/oi'
OI_SRC = 'outputs/data/tradexyz_oi_rolling.csv'
LIQ_SRC = 'outputs/data/tradexyz_daily_liquidations_q2.csv'
START, END = datetime(2026, 1, 1), datetime(2026, 6, 30)


# The book's OI series carries a one-day needle our S3/ASXN series do not: a
# snapshot-derived reading, digitised off the reference chart. The `ref`
# variant patches it in so the two charts can be shown side by side.
REF_PATCH = {'2026-03-24': 2.839}


def load(reference=False):
    oi = pd.read_csv(OI_SRC, parse_dates=['date'])
    # the snapshot file stamps each reading with the prior day
    oi['date'] = oi.date + pd.Timedelta(days=1)
    oi = oi[oi.date.between(START, END)]
    if reference:
        oi = oi.copy()
        for day, val in REF_PATCH.items():
            oi.loc[oi.date == pd.Timestamp(day), 'oi'] = val
    liq = pd.read_csv(LIQ_SRC, parse_dates=['date'])
    liq = liq[liq.date.between(START, END)]
    return oi, liq


def draw_chart(oi, liq):
    setup_font()
    fig, (ax, axl) = plt.subplots(
        2, 1, figsize=(10.9, 5.4), dpi=150, sharex=True,
        gridspec_kw=dict(height_ratios=[2, 1]))
    fig.patch.set_alpha(0)
    for a in (ax, axl):
        base_axes(a)

    ax.axhline(3, color=BODY, linewidth=1.2, linestyle=(0, (6, 4)), zorder=2)
    ax.text(END, 3.06, '$3B  ', fontsize=11, color=BODY, ha='right',
            va='bottom', zorder=5)
    ax.plot(oi.date, oi.oi, color=POINT, linewidth=1.8, zorder=4)

    peak = oi.loc[oi.oi.idxmax()]
    ax.plot([peak.date], [peak.oi], marker='o', markersize=5, color=POINT,
            zorder=5)
    ax.text(peak.date - pd.Timedelta(days=2), 2.30,
            f'Peak ${peak.oi:.2f}B\n{peak.date:%b %-d}', fontsize=11,
            color=POINT, ha='right', va='top', linespacing=1.35, zorder=5)
    ax.text(START, 2.72, '  Venue OI (Long+Short Notional)', fontsize=12,
            color=POINT, ha='left', va='top', zorder=5)

    ax.set_ylim(0, 3.28)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['$0B', '$1B', '$2B', '$3B'])
    ax.tick_params(axis='y', labelsize=13, pad=6)

    axl.vlines(liq.date, 0, liq.liquidated_usd / 1e6, color=RED,
               linewidth=2.4, zorder=3)
    axl.text(START, 104, '  Daily Liquidations', fontsize=12, color=RED,
             ha='left', va='top', zorder=5)
    axl.text(START, 78, '  Liquidation File Covers Q2 Only', fontsize=11,
             color=NOTE, ha='left', va='top', zorder=5)

    axl.set_ylim(0, 112)
    axl.set_yticks([0, 50, 100])
    axl.set_yticklabels(['$0M', '$50M', '$100M'])
    axl.tick_params(axis='y', labelsize=13, pad=6)
    axl.set_xlim(START, END)
    axl.xaxis.set_major_locator(mdates.MonthLocator())
    axl.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    axl.tick_params(axis='x', labelsize=12, pad=5, length=5, width=1,
                    color=NOTE)
    plt.setp(axl.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.12)
    return fig


if __name__ == '__main__':
    import tradexyz_q2_volume_by_asset_class as base
    base.OUT_DIR = OUT_DIR
    for ref in (False, True):
        oi, liq = load(reference=ref)
        name = 'oi_liquidations_ref' if ref else 'oi_liquidations'
        print(name, 'OI %.3f -> %.3f, peak %.3f on %s, first $3B %s' % (
            oi.oi.iloc[0], oi.oi.iloc[-1], oi.oi.max(),
            oi.loc[oi.oi.idxmax(), 'date'].date(),
            oi[oi.oi > 3].date.min().date()))
        save(draw_chart(oi, liq), name)
