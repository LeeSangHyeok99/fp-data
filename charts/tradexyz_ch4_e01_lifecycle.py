"""Trade[XYZ] ch4 e01: pre-IPO perpetual lifecycle diagram, HRC theme redraw.

Layout coordinates are lifted from the reference SVG (962.2368 x 589.6368 pt),
so the axes work directly in reference points with y inverted. Title, subtitle
and source footer are dropped per house chart rules.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

sys.path.append('.claude/skills/design/hrc')
from config import DPI  # noqa: E402

OUT_DIR = Path('outputs/charts/tradexyz/ch4')

# --- HRC palette (dark spec) -------------------------------------------------
TITLE = '#D9D9D9'    # headline text
BODY = '#9CA3AF'     # sub-title and body text
NOTE = '#6D6D6D'     # source / date / note text, settlement branch
POINT = '#F9BD29'    # point colour: funding step, trader risk, live path note
sys.path.append('charts')
from tradexyz_ch4_palette import MARKET_COLORS as SWATCH  # noqa: E402

# --- crop window in reference points -----------------------------------------
X0, X1 = 30.0, 802.0
Y0, Y1 = 100.0, 545.0


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'
    else:
        plt.rcParams['font.family'] = 'Arial'


def rbox(ax, x0, y0, x1, y1, edge, face, lw=1.4, dashed=False, pad=6.6):
    ax.add_patch(FancyBboxPatch(
        (x0 + pad, y0), (x1 - x0) - 2 * pad, y1 - y0,
        boxstyle=f'round,pad={pad},rounding_size={pad}',
        linewidth=lw, edgecolor=edge, facecolor=face,
        linestyle=(0, (4, 2.5)) if dashed else '-', zorder=2,
    ))


def block(ax, x, y, lines, size, color, leading, weight='regular', ha='left'):
    for i, line in enumerate(lines):
        ax.text(x, y + i * leading, line, fontsize=size, color=color,
                fontweight=weight, ha=ha, va='baseline', zorder=4)


def draw_chart():
    setup_font()
    fig = plt.figure(figsize=((X1 - X0) / 72, (Y1 - Y0) / 72), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(X0, X1)
    ax.set_ylim(Y1, Y0)          # inverted: reference SVG y grows downward
    ax.axis('off')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # --- header note ---------------------------------------------------------
    ax.text(42.3, 116, 'All Three Q2 Markets Took This Path',
            fontsize=9.4, fontweight='bold', color=POINT, va='baseline')

    # --- stage boxes ---------------------------------------------------------
    rbox(ax, 41.75, 134.51, 370.21, 243.66, BODY, (1, 1, 1, 0.04))
    rbox(ax, 461.45, 134.51, 789.90, 243.66, BODY, (1, 1, 1, 0.04))

    ax.text(59.7, 155.4, 'STAGE 1 · PRE-LISTING', fontsize=9.4,
            fontweight='bold', color=POINT, va='baseline')
    ax.text(60.0, 175.0, 'Priced Entirely By Its Own Book', fontsize=13,
            fontweight='bold', color=TITLE, va='baseline')
    block(ax, 60.0, 193.0, [
        "Oracle is a 30-minute EWMA advanced by the",
        "market's own impact-price difference. No external feed.",
        "Funding multiplier 0.005x.  Discovery Bounds active.",
    ], 9.6, BODY, 11.2)

    ax.text(480.2, 155.4, 'STAGE 2 · CONVERTED', fontsize=9.4,
            fontweight='bold', color=POINT, va='baseline')
    ax.text(479.7, 175.0, 'A Standard Equity Perpetual', fontsize=13,
            fontweight='bold', color=TITLE, va='baseline')
    block(ax, 479.7, 193.0, [
        'External oracle takes over pricing.',
        'Funding multiplier 0.5x.',
        'Discovery Bounds widen or lift per market.',
    ], 9.6, BODY, 11.2)

    # --- conversion box ------------------------------------------------------
    rbox(ax, 383.89, 127.39, 453.23, 250.77, TITLE, 'none', lw=1.6)
    ax.text(418.56, 152.5, 'CONVERSION', fontsize=8.6, fontweight='bold',
            color=TITLE, ha='center', va='baseline')
    block(ax, 418.56, 167.4, ['first', 'regular-way', 'Nasdaq', 'session'],
          8.4, BODY, 9.2, ha='center')
    ax.text(418.56, 231.0, '100x', fontsize=15, fontweight='bold',
            color=POINT, ha='center', va='baseline')
    ax.text(418.56, 244.4, 'Funding Step', fontsize=8, color=POINT,
            ha='center', va='baseline')

    for x0 in (372.03, 455.06):
        ax.add_patch(FancyArrowPatch(
            (x0 - 1.5, 189.08), (x0 + 10.5, 189.08), arrowstyle='-|>',
            mutation_scale=11, linewidth=1.8, color=POINT, zorder=3))

    # --- settlement branch ---------------------------------------------------
    elbow = PathPatch(
        MPath([(418.56, 255.05), (418.56, 290.01), (421.56, 293.01),
               (455.0, 293.01)],
              [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3, MPath.LINETO]),
        fill=False, edgecolor=NOTE, linewidth=1.5,
        linestyle=(0, (4, 2.5)), zorder=2)
    ax.add_patch(elbow)
    ax.add_patch(FancyArrowPatch((455.0, 293.01), (460.5, 293.01),
                                 arrowstyle='-|>', mutation_scale=9,
                                 linewidth=1.5, color=NOTE, zorder=3))
    block(ax, 333.7, 259.0, ['if the issuer', 'never lists'], 8.6, NOTE, 10.2,
          weight='normal')

    rbox(ax, 370.21, 295.86, 789.90, 386.02, NOTE, 'none', lw=1.3, dashed=True)
    ax.text(388.7, 314.6, 'CONFIGURED ON ALL THREE, EXERCISED ON NONE',
            fontsize=8.6, fontweight='bold', color=NOTE, va='baseline')
    ax.text(388.5, 328.6, 'The Settlement Path', fontsize=12.5,
            fontweight='bold', color=NOTE, va='baseline')
    block(ax, 388.5, 340.0, [
        'Outside Launch Date, then a fixed 60-day Settlement Period.',
        'Default price is a TWAP of the market from launch to settlement.',
        'Alternative settlement for transaction, extended-market and',
        'adverse events. CBRS instance: ODL May 30, settle by Jul 30.',
    ], 9.2, NOTE, 11.1)

    # --- trader risk ---------------------------------------------------------
    rbox(ax, 41.75, 295.86, 288.09, 386.02, POINT,
         (0.976, 0.741, 0.161, 0.09), lw=1.2)
    ax.text(60.0, 314.6, 'TRADER RISK', fontsize=8.6, fontweight='bold',
            color=POINT, va='baseline')
    block(ax, 60.0, 333.4, [
        'The mark-price step at conversion, when pricing',
        'switches from the internal mechanism to the',
        'external oracle. It is the one discontinuity a',
        'position carries through the whole lifecycle.',
    ], 9.2, BODY, 11.1)

    # --- market table --------------------------------------------------------
    ax.text(42.3, 421.5, 'The Three Markets', fontsize=11.5,
            fontweight='bold', color=TITLE, va='baseline')
    ax.text(42.3, 437.4,
            'Parameters as configured at launch, dates UTC. Every contract is '
            'a cash-settled linear perpetual, 5x maximum leverage on isolated '
            'margin, trading 24/7.',
            fontsize=9, color=NOTE, va='baseline')

    cols = [('Market', 42.3), ('OI Cap', 204.0), ('Reference', 288.2),
            ('Bound', 379.6), ('Launch', 448.0), ('Converted', 524.4),
            ('Nasdaq Open', 616.3)]
    for label, x in cols:
        ax.text(x, 460.9, label, fontsize=8.8, fontweight='bold',
                color=NOTE, va='baseline')
    ax.plot([41.75, 735.16], [469.54, 469.54], color=NOTE, linewidth=0.9,
            alpha=0.5, zorder=1)

    rows = [
        ('CBRS', 'Cerebras', '$100M', '$175', '±25%', 'May 1', 'May 14', '$350.00'),
        ('SPCX', 'SpaceX', '$150M', '$150', '±20%', 'May 17', 'Jun 12', '$150.00'),
        ('QNT', 'Quantinuum', '$20M', '$75', '±25%', 'May 28', 'Jun 4', '$68.00'),
    ]
    for i, (tick, name, *vals) in enumerate(rows):
        y = 488.0 + i * 20.88
        ax.add_patch(Rectangle((41.75, y - 7.6), 13.69, 9.49,
                               facecolor=SWATCH[tick], edgecolor='none',
                               zorder=3))
        ax.text(62.5, y, tick, fontsize=9.8, fontweight='bold', color=TITLE,
                va='baseline')
        ax.text(108.3, y, name, fontsize=8.8, color=NOTE, va='baseline')
        for val, (_, x) in zip(vals, cols[1:]):
            ax.text(x, y, val, fontsize=9.4, color=TITLE, va='baseline')

    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e01_lifecycle_diagram.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    # preview on the HRC surface colour for visual QA
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e01.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
