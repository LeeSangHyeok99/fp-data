"""Trade[XYZ] ch4 e02 / e10 / e11: the three reference tables, HRC dark theme.

Content is taken verbatim from the reference markdown that ships beside each
CSV. Headings, the lead paragraph and the source footer are dropped per house
rules, so each output is the table alone on a transparent ground.
"""
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI  # noqa: E402
from tradexyz_ch4_palette import (  # noqa: E402
    TITLE, BODY, NOTE, POINT, MARKET_COLORS)

OUT_DIR = Path('outputs/charts/tradexyz/ch4')

PAD_X = 14.0          # pt of canvas margin left/right
PAD_Y = 12.0


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def lit(t):
    """Escape $ so a cell with two of them is not parsed as mathtext, which
    would silently render that line in DejaVu instead of SUIT."""
    return t.replace('$', r'\$')


def canvas(width_pt, height_pt):
    """Figure whose axes span the whole canvas in points, y growing downward."""
    fig = plt.figure(figsize=(width_pt / 72, height_pt / 72), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width_pt)
    ax.set_ylim(height_pt, 0)
    ax.axis('off')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    return fig, ax


def rule(ax, x0, x1, y, color=NOTE, lw=0.9, alpha=0.55):
    ax.plot([x0, x1], [y, y], color=color, linewidth=lw, alpha=alpha, zorder=2)


def save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'{name}.{ext}', dpi=DPI, facecolor='none',
                    edgecolor='none', transparent=True)
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / f'_preview_{name}.png', dpi=DPI, facecolor='#1a1a1a')
    plt.close(fig)


# =============================================================================
# E2. Market parameters
# =============================================================================
E02_COLS = [
    ('Market', 14.0),
    ('OI Cap', 200.0),
    ('Initial Reference', 272.0),
    ('Discovery Bound', 386.0),
    ('Launch (UTC)', 496.0),
    ('Conversion (UTC)', 590.0),
    ('Funding Multiplier, Pre / Post', 706.0),
]
E02_ROWS = [
    ('CBRS', 'Cerebras', ['$100M', '$175', '±25%', '2026-05-01', '2026-05-14',
                          '0.005x / 0.5x']),
    ('QNT', 'Quantinuum', ['$20M', '$75', '±25%', '2026-05-28', '2026-06-04',
                           '0.005x / 0.5x']),
    ('SPCX', 'SpaceX', ['$150M', '$150', '±20%', '2026-05-17', '2026-06-12',
                        '0.005x / 0.5x']),
]


def draw_e02():
    W, ROW_H = 900.0, 34.0
    H = PAD_Y * 2 + 26 + ROW_H * len(E02_ROWS)
    fig, ax = canvas(W, H)

    y = PAD_Y + 12
    for label, x in E02_COLS:
        ax.text(x, y, lit(label), fontsize=11, fontweight='bold', color=NOTE,
                va='baseline', zorder=3)
    rule(ax, PAD_X, W - PAD_X, y + 9)

    for i, (ticker, company, vals) in enumerate(E02_ROWS):
        y = PAD_Y + 26 + ROW_H * i + ROW_H / 2 + 4
        ax.add_patch(Rectangle((PAD_X, y - 12), 9, 9,
                               facecolor=MARKET_COLORS[ticker],
                               edgecolor='none', zorder=3))
        ax.text(32, y, lit(ticker), fontsize=13, fontweight='bold', color=TITLE,
                va='baseline', zorder=3)
        ax.text(84, y, lit(company), fontsize=11.5, color=NOTE, va='baseline',
                zorder=3)
        for val, (_, x) in zip(vals, E02_COLS[1:]):
            ax.text(x, y, lit(val), fontsize=12.5, color=TITLE, va='baseline',
                    zorder=3)
        if i < len(E02_ROWS) - 1:
            rule(ax, PAD_X, W - PAD_X, y + ROW_H / 2 - 4, alpha=0.22)
    return fig


# =============================================================================
# E10. Launch-over-launch maturation
# =============================================================================
E10_HEAD = ['CBRS (Cerebras)', 'QNT (Quantinuum)', 'SPCX (SpaceX)']
E10_ROWS = [
    ('row', 'Launch To Conversion (UTC)',
     ['2026-05-01 to 05-14', '2026-05-28 to 06-04', '2026-05-17 to 06-12']),
    ('group', 'Demand', None),
    ('row', 'Pre-Listing Volume (All Observed Days To The Open)',
     ['$47.9M', '$18.4M', '$794.3M']),
    ('row', 'Daily Average (Window)',
     ['$3.69M (13d)', '$2.62M (7d)', '$30.6M (26d)']),
    ('row', 'Conversion-Day Volume (Full UTC Day)',
     ['$281.4M', '$54.6M', '$1.38B']),
    ('row', 'Conversion-Day ÷ Pre-Listing', ['5.87×', '2.97×', '1.74×']),
    ('group', 'Participation', None),
    ('row', 'Unique Wallets (Pre-Listing Window)',
     ['2,600', '1,690', '17,882']),
    ('row', 'Top-10 Wallet Share (Taker Volume)', ['15.5%', '19.7%', '25.9%']),
    ('row', 'Gini Coefficient (Taker Volume)', ['0.840', '0.820', '0.946']),
    ('group', 'Market Quality', None),
    ('row', 'Realized Vol (Annualized)', ['282%', '190%', '60%']),
    ('row', 'Launch-Phase Median Spread', ['110 bps', '64 bps', '7.4 bps']),
    ('row', '$100k Slippage (Launch Phase)', ['473 bps', '327 bps', '51 bps']),
]


def draw_e10():
    W, ROW_H, GROUP_H = 880.0, 30.0, 34.0
    col_x = [430.0, 570.0, 710.0]
    H = (PAD_Y * 2 + 30
         + sum(GROUP_H if k == 'group' else ROW_H for k, _, _ in E10_ROWS))
    fig, ax = canvas(W, H)

    y = PAD_Y + 14
    ax.text(PAD_X, y, 'Metric', fontsize=11, fontweight='bold', color=NOTE,
            va='baseline', zorder=3)
    for head, x in zip(E10_HEAD, col_x):
        ticker = head.split()[0]
        ax.text(x, y, lit(head), fontsize=11, fontweight='bold',
                color=MARKET_COLORS[ticker], va='baseline', zorder=3)
    rule(ax, PAD_X, W - PAD_X, y + 10)

    y = PAD_Y + 30
    for kind, label, vals in E10_ROWS:
        if kind == 'group':
            y += GROUP_H
            ax.text(PAD_X, y - 9, lit(label), fontsize=11, fontweight='bold',
                    color=POINT, va='baseline', zorder=3)
            rule(ax, PAD_X, W - PAD_X, y - 4, color=POINT, lw=0.8, alpha=0.35)
            continue
        y += ROW_H
        ax.text(PAD_X, y - 9, lit(label), fontsize=12, color=BODY, va='baseline',
                zorder=3)
        for val, x in zip(vals, col_x):
            ax.text(x, y - 9, lit(val), fontsize=12.5, color=TITLE, va='baseline',
                    zorder=3)
    return fig


# =============================================================================
# E11. The listing queue
# =============================================================================
E11_COLS = [('Company', 14.0, 120), ('Business', 150.0, 26),
            ('Reported Valuation (Window)', 330.0, 42),
            ('Listing Status (As Of Late July 2026)', 640.0, 54)]
E11_ROWS = [
    ('OpenAI', 'Foundation-model developer (ChatGPT)',
     '$852B post-money (March 2026 financing, company-stated); press reports '
     'a ~$1T listing target with a raise near $60B',
     'Confidential draft S-1 submitted to the SEC 2026-06-08. Original window '
     'Q3-Q4 2026; July 2026 reporting describes a lean toward 2027. Timing '
     'undecided per the company.'),
    ('Anthropic', 'Foundation-model developer (Claude)',
     '$965B (Series H, May 2026, closed)',
     'Confidential S-1 filed 2026-06-01. October 2026 Nasdaq target per press, '
     'Goldman Sachs / JPMorgan / Morgan Stanley leading, raise above $60B.'),
    ('Databricks', 'Enterprise data and AI platform',
     '$134B (Series L, closed); round talks reported at $165-175B '
     '(The Information, June 2026)',
     'No public S-1 as of early July 2026. CEO Ali Ghodsi called 2026 "a '
     'terrible year to go public" (Bloomberg TV, 2026-06-04) and pointed to '
     '2027 at the earliest.'),
    ('Stripe', 'Payments infrastructure',
     '$159B (employee and shareholder tender, February 2026)',
     'No S-1 filed and no announced IPO as of mid-June 2026; tender offers '
     'serve as the liquidity valve. Analyst consensus points to 2027 or later.'),
    ('Discord', 'Consumer chat and community platform',
     'Reported listing target near $15B; secondary-market marks near $8.5B '
     '(mid-June 2026)',
     'Confidential draft S-1 filed January 2026 per press, Goldman Sachs and '
     'JPMorgan reportedly engaged; no ticker, price range, or listing date as '
     'of late June 2026. Per press, unconfirmed.'),
]


def draw_e11():
    W, LINE_H, ROW_PAD = 1000.0, 15.5, 15.0
    wrapped = [[textwrap.wrap(cell, E11_COLS[c][2]) or ['']
                for c, cell in enumerate(row)] for row in E11_ROWS]
    heights = [max(len(c) for c in row) * LINE_H + ROW_PAD for row in wrapped]
    H = PAD_Y * 2 + 30 + sum(heights)
    fig, ax = canvas(W, H)

    y = PAD_Y + 14
    for label, x, _ in E11_COLS:
        ax.text(x, y, lit(label), fontsize=11, fontweight='bold', color=NOTE,
                va='baseline', zorder=3)
    rule(ax, PAD_X, W - PAD_X, y + 10)

    y = PAD_Y + 30
    for i, (row, h) in enumerate(zip(wrapped, heights)):
        top = y + 15
        for c, lines in enumerate(row):
            x = E11_COLS[c][1]
            bold = 'bold' if c == 0 else 'normal'
            color = TITLE if c in (0, 2) else BODY
            size = 12.5 if c == 0 else 11.5
            for k, line in enumerate(lines):
                ax.text(x, top + k * LINE_H, lit(line), fontsize=size,
                        fontweight=bold, color=color, va='baseline', zorder=3)
        y += h
        if i < len(wrapped) - 1:
            rule(ax, PAD_X, W - PAD_X, y, alpha=0.22)
    return fig


if __name__ == '__main__':
    setup_font()
    save(draw_e02(), 'e02_params_table')
    save(draw_e10(), 'e10_maturation_table')
    save(draw_e11(), 'e11_pipeline_table')
    print('saved', OUT_DIR)
