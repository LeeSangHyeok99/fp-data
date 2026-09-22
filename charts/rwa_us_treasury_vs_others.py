"""
Tokenized US Treasuries as a share of total tokenized RWAs (ex-stablecoins)
Four Pillars design theme

US Treasury Debt만 색으로 구분하고, 나머지 11개 자산군은 하나의 색으로 통합.
Data: sources/rwa-token-timeseries-export-1785221426501.csv (rwa.xyz export)
Colors: rwa.xyz asset_classes palette (US Treasury Debt = #0d2e53)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from config import COLORS, apply_style, setup_font, save_chart

SRC = 'sources/rwa-token-timeseries-export-1785221426501.csv'
OUTPUT_DIR = 'outputs/charts/rwa/market'
START_DATE = '2024-01-01'

TREASURY = 'US Treasury Debt'
OTHER_COLS = [
    'non-US Government Debt', 'Corporate Credit', 'Stocks', 'Private Equity',
    'Real Estate', 'Commodities', 'Diversified Credit', 'Asset-Backed Credit',
    'Active Strategies', 'Specialty Finance', 'Venture Capital',
]

C_TREASURY = '#0d2e53'   # rwa.xyz US Treasury Debt navy
C_OTHERS = '#7d7d7e'     # 나머지 전체 통합
C_LINE = '#7aa6d6'

TICK_FONTSIZE = 18       # y축
TICK_FONTSIZE_X = 16     # x축 (y축보다 2pt 작게)

df = pd.read_csv(SRC)
df['Date'] = pd.to_datetime(df['Date'])
for col in [TREASURY] + OTHER_COLS:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / 1e9

df = df[df['Date'] >= START_DATE].sort_values('Date')
df['Others'] = df[OTHER_COLS].sum(axis=1)
df['Total'] = df['Others'] + df[TREASURY]
assert len(df) > 900, f'unexpected row count: {len(df)}'
assert df['Total'].iloc[-1] > 30, f'total looks wrong: {df["Total"].iloc[-1]}'


def draw(figsize=(10.67, 4.67)):
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)

    dates = df['Date']
    ax.fill_between(dates, 0, df['Others'], color=C_OTHERS,
                    alpha=0.95, linewidth=0, zorder=2)
    ax.fill_between(dates, df['Others'], df['Total'], color=C_TREASURY,
                    alpha=0.95, linewidth=0, zorder=2)
    ax.plot(dates, df['Total'], color=C_LINE, linewidth=1.8, alpha=0.9, zorder=4)

    ax.set_xlim(dates.iloc[0], dates.iloc[-1])
    ax.set_ylim(0, 40)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30, 40]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    apply_style(fig, ax, 'stacked')
    # 축 라벨 크기 축소, x/y 동일 사이즈로 통일
    ax.tick_params(axis='y', labelsize=TICK_FONTSIZE)
    ax.tick_params(axis='x', labelsize=TICK_FONTSIZE_X)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    last = df.iloc[-1]
    share = last[TREASURY] / last['Total'] * 100
    print(f'{last["Date"].date()}  total ${last["Total"]:.2f}B  '
          f'treasury ${last[TREASURY]:.2f}B ({share:.1f}%)  '
          f'others ${last["Others"]:.2f}B')

    fig = draw()
    png, svg = save_chart(fig, 'rwa_us_treasury_vs_others', output_dir=OUTPUT_DIR)
    print(f'  -> {png}\n  -> {svg}')
    plt.close(fig)
