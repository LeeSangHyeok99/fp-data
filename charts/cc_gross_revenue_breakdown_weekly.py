"""Collector Crypt weekly gross revenue by pack category (stacked bar).

Data: outputs/data/cc_gross_revenue_breakdown_weekly.csv, extracted from the
Blockworks Research "Collector Crypt: Gross Revenue Breakdown" chart (weekly).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, gradient_rounded_bar, COLORS, DPI

setup_font()

df = pd.read_csv('outputs/data/cc_gross_revenue_breakdown_weekly.csv',
                 parse_dates=['week_start'])

# Source series and colors follow the Blockworks legend.
SERIES = [
    ('pokemon_packs', '#d78c2f'),
    ('one_piece_packs', '#0a32f6'),
    ('sports_packs', '#5bc398'),
    ('riftbound_packs', '#fecb37'),
    ('sealed_packs', '#b05dcf'),
    ('anime_packs', '#467f23'),
    ('comic_book_packs', '#356956'),
    ('watches_packs', '#e0256b'),
    ('dragon_ball_packs', '#fb4849'),
    ('packs_credit_card', '#fb5972'),
    ('launchpad', '#b36420'),
    ('marketplace_royalties', '#623571'),
]

# Keep the five largest series over the displayed period. Aggregate every
# remaining category row-wise so the chart and external legend both show
# at most five named series plus Others.
series_columns = [column for column, _ in SERIES]
top_five = set(df[series_columns].sum().nlargest(5).index)
other_columns = [column for column in series_columns if column not in top_five]
df['others'] = df[other_columns].sum(axis=1)
PLOT_SERIES = [item for item in SERIES if item[0] in top_five]
PLOT_SERIES.append(('others', '#777b80'))

OUTPUT_DIR = 'outputs/charts/collector_crypt/revenue'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(12.5, 6.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bottom = pd.Series(0.0, index=df.index)
xs = mdates.date2num(df['week_start'])
for col, color in PLOT_SERIES:
    # 세그먼트별 세로 그라데이션 (원색을 중간에 두고 아래 어둡게, 위 밝게)
    for xi, b, v in zip(xs, bottom, df[col]):
        gradient_rounded_bar(ax, x_center=xi, width=5.6, height=b + v, color=color,
                             floor=0.86, ceil=1.14, round_top=False, y0=b)
    bottom = bottom + df[col]

ax.set_ylim(0, 70)
ax.set_yticks([0, 20, 40, 60])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(df['week_start'].min() - pd.Timedelta(days=3.5),
            df['week_start'].max() + pd.Timedelta(days=3.5))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=16, length=0, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=16, length=6, width=1, pad=8, rotation=45,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation_mode='anchor')
fig.tight_layout()

for fmt in ('png', 'svg'):
    fig.savefig(f'{OUTPUT_DIR}/cc_gross_revenue_breakdown_weekly.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(f'{OUTPUT_DIR}/cc_gross_revenue_breakdown_weekly.svg')
