"""ch6 e610: basis at the opening cross against basis at session close.

Left panel is the dumbbell per conversion, right panel is how long each market
took to get inside 100 bps.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, MARKET_COLORS, base_axes, save, setup_font)

ORDER = ['CBRS', 'QNT', 'SPCX']


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e610_convergence_three_data.csv')
    df = df.set_index('market').loc[ORDER].reset_index()
    df['initial'] = df['initial_basis_bps'].abs()
    df['final'] = df['final_basis_bps'].abs()

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 5.4), dpi=DPI,
        gridspec_kw=dict(width_ratios=[2.5, 1], wspace=0.16))
    fig.patch.set_alpha(0)
    base_axes(ax, axis='x')
    base_axes(ax2, axis='x')

    for i, r in df.iterrows():
        c = MARKET_COLORS[r['market']]
        ax.plot([r['final'], r['initial']], [i] * 2, color=c, linewidth=6,
                alpha=0.45, solid_capstyle='round', zorder=3)
        ax.plot(r['final'], i, 'o', color=c, markersize=13, zorder=5)
        ax.plot(r['initial'], i, 'o', color='none', markeredgecolor=c,
                markeredgewidth=2.4, markersize=13, zorder=5)
        ax.text(r['final'], i - 0.26, f"{r['final']:.0f} bps", fontsize=12,
                color=TITLE, ha='center', va='bottom', zorder=5)
        ax.text(r['initial'], i - 0.26, f"{r['initial']:.0f}", fontsize=12,
                color=c, ha='center', va='bottom', zorder=5)
        ax.text(-46, i, r['market'], fontsize=14, color=c, ha='left',
                va='center', zorder=5)

        ax2.barh(i, r['t_to_100bps_min'], color=c, height=0.52, zorder=3)
        ax2.text(r['t_to_100bps_min'] + 1.4, i,
                 f"{int(r['t_to_100bps_min'])} min", fontsize=12, color=TITLE,
                 ha='left', va='center', zorder=5)

    ax.text(-46, 2.62, 'Filled Dot Is At Session Close, Open Dot Is At The '
            'Opening Cross.', fontsize=11, color=NOTE, ha='left', va='center',
            zorder=5)

    ax.set_xlim(-48, 400)
    ax.set_xticks([0, 100, 200, 300, 400])
    ax.set_ylim(2.8, -0.7)
    ax.set_yticks([])
    ax.set_xlabel('Absolute Basis To The Traditional Tape (bps)', fontsize=12,
                  color=NOTE, labelpad=10)

    ax2.set_xlim(0, 50)
    ax2.set_xticks([0, 10, 20, 30, 40, 50])
    ax2.set_ylim(2.8, -0.7)
    ax2.set_yticks([])
    ax2.set_xlabel('Minutes To Reach 100 bps', fontsize=12, color=NOTE,
                   labelpad=10)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e610_convergence_three')
