"""ch6 e65: median quoted spread per market, Trade[XYZ] RWA against HL crypto.

Strip plot on a log axis with the same data as a CDF underneath. The RWA book
is the subject, so it takes the point colour; the crypto cross-section is the
grey comparison.
"""
import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, BODY, NOTE, POINT, DIM, base_axes, save, setup_font)

# muted Hyperliquid mint: keeps the venue's identity without out-shouting the
# point colour the chart is actually about
HL_MINT = '#4E8C82'

ROWS = [('xyz_rwa', 'Trade[XYZ] RWA', POINT, 1),
        ('hl_crypto', 'Hyperliquid Crypto Perps', HL_MINT, 0)]
TICKS = [0.5, 1, 2, 5, 10, 25, 50, 100, 250]


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e65_rwa_vs_crypto_data.csv')
    rng = np.random.default_rng(6)

    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(12.6, 7.2), dpi=DPI,
        gridspec_kw=dict(height_ratios=[2.6, 1], hspace=0.42))
    fig.patch.set_alpha(0)

    for a in (ax, ax2):
        base_axes(a, axis='x')
        a.set_xscale('log')
        a.set_xlim(0.35, 320)
        a.set_xticks(TICKS)
        a.set_xticklabels([f'{t:g}' for t in TICKS])
        a.xaxis.set_minor_locator(plt.NullLocator())

    for book, label, color, y in ROWS:
        s = df.loc[df['book'] == book, 'median_spread_bps']
        ax.scatter(s, y + rng.uniform(-0.17, 0.17, len(s)), s=26, color=color,
                   alpha=0.75, linewidths=0, zorder=3)
        med = s.median()
        ax.plot([med, med], [y - 0.30, y + 0.30], color=color, linewidth=2.6,
                zorder=4)
        ax.text(med, y + 0.36, f'Median {med:.1f} bps   n={len(s)}',
                fontsize=12, color=color, ha='center', va='bottom', zorder=5)
        ax.text(0.36, y + 0.36, label, fontsize=13, color=color, ha='left',
                va='bottom', zorder=5)

    ax.set_ylim(-0.62, 1.72)
    ax.set_yticks([])

    for book, label, color, _ in ROWS:
        s = np.sort(df.loc[df['book'] == book, 'median_spread_bps'].values)
        grid = np.logspace(np.log10(s[0]), np.log10(s[-1]), 500)
        y = np.searchsorted(s, grid, 'right') / len(s) * 100
        k = 41  # boxcar over the log grid; monotone in, monotone out
        y = np.convolve(np.pad(y, k // 2, mode='edge'), np.ones(k) / k, 'valid')
        ax2.plot(grid, y, color=color, linewidth=2.0, zorder=3)
    ax2.set_ylim(0, 108)
    ax2.set_yticks([0, 50, 100])
    ax2.set_yticklabels(['0%', '50%', '100%'])
    ax2.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
             linestyle=(0, (3.7, 1.6)))
    ax2.text(0.36, 96, 'Cumulative Share Of Markets', fontsize=12, color=NOTE,
             ha='left', va='top', zorder=5)
    ax2.text(300, 8, '90th Percentile: 16.1 bps RWA Against 11.1 bps Crypto.',
             fontsize=12, color=BODY, ha='right', va='bottom', zorder=5)
    ax2.text(300, -34, 'Median Quoted Spread Per Market, Final Week Of Q2'
             '  (bps, Log Scale)', fontsize=12, color=NOTE, ha='right',
             va='top', zorder=5)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e65_rwa_vs_crypto')
