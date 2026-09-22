"""Trade[XYZ] ch4 e08: final pre-listing mark per venue vs the SpaceX open.

Source data ships with the reference (e08_spcx_scorecard_data.csv).
Title, subtitle, legend and source footer dropped per house rules; the legend
is replaced by direct labels on the top row's two markers.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI  # noqa: E402
from tradexyz_ch4_palette import TITLE, BODY, NOTE, VENUE_COLORS  # noqa: E402

DATA = Path('outputs/data/tradexyz_ch4')
OUT_DIR = Path('outputs/charts/tradexyz/ch4')


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e08_spcx_scorecard.csv')

    fig, ax = plt.subplots(figsize=(11.5, 5.4), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    ax.grid(True, axis='x', color=NOTE, alpha=0.35, linewidth=0.9,
            linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)

    n = len(df)
    for i, r in df.iterrows():
        y = n - 1 - i                       # rank 1 at the top
        color = VENUE_COLORS[r['display_name']]
        lo, hi = r['vs_vwap30_pct_published'], r['vs_open_pct_published']
        ax.plot([lo, hi], [y, y], color=color, linewidth=2.6, alpha=0.55,
                zorder=3, solid_capstyle='round')
        ax.plot([lo], [y], marker='o', markersize=11, markerfacecolor='none',
                markeredgecolor=color, markeredgewidth=2.0, zorder=4)
        ax.plot([hi], [y], marker='o', markersize=11, color=color, zorder=4)
        ax.text(lo - 0.35, y, f'+{lo:.1f}%', fontsize=12, color=BODY,
                ha='right', va='center', zorder=5)
        ax.text(hi + 0.35, y, f'+{hi:.1f}%', fontsize=12.5, color=TITLE,
                fontweight='bold', ha='left', va='center', zorder=5)
        ax.text(-0.6, y + 0.18, r['display_name'], fontsize=13, color=TITLE,
                ha='right', va='center', zorder=5)
        ax.text(-0.6, y - 0.20, f"Mark ${r['final_mark_usd_per_share']:.2f}",
                fontsize=10.5, color=NOTE, ha='right', va='center', zorder=5)

    ax.text(df['vs_open_pct_published'].iloc[0] + 2.4, n - 1, 'Closest',
            fontsize=11, color=NOTE, ha='left', va='center')
    ax.text(df['vs_open_pct_published'].iloc[-1] + 2.4, 0, 'Widest',
            fontsize=11, color=NOTE, ha='left', va='center')

    # --- direct marker labels (in place of a legend) -------------------------
    top = n - 1
    ax.annotate('vs First-30-Min VWAP $160.97',
                xy=(df['vs_vwap30_pct_published'].iloc[0], top),
                xytext=(4.6, top + 0.62), fontsize=11, color=BODY,
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-', color=NOTE, linewidth=0.8))
    ax.annotate('vs Nasdaq Open $150.00',
                xy=(df['vs_open_pct_published'].iloc[0], top),
                xytext=(15.6, top + 0.62), fontsize=11, color=TITLE,
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-', color=NOTE, linewidth=0.8))

    ax.set_ylim(-0.7, n - 0.15)
    ax.set_yticks([])
    ax.set_xlim(0, 21)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xticklabels(['0%', '+5%', '+10%', '+15%', '+20%'])
    ax.text(1.3, -1.02, '0% = Realized Print', fontsize=11, color=NOTE,
            ha='left', va='top')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e08_spcx_scorecard.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e08.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
