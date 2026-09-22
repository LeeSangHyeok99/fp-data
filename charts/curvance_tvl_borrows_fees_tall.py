import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('sources/figure09_curvance_tvl_borrows_fees.csv',
                 parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})

COLOR_TVL = '#5C55EA'      # 바이올렛
COLOR_BORROWS = '#8B7CF6'  # 라이트 바이올렛
COLOR_FEES = '#A1B4ED'     # 페리윙클

setup_font()

FIGSIZE = (5.8, 7.1)  # 세로형 (3개를 한 카드에 나란히 배치)


def style_axes(fig, ax, dates):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 4, 6, 8]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(dates.min(), dates.max())
    apply_style(fig, ax, 'area')
    ax.tick_params(axis='y', labelsize=16)
    ax.tick_params(axis='x', labelsize=14)


def line_area_chart(series, color, y_ticks, y_labels, y_max, out_dir, filename):
    d = df[series.notna()]
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=150)
    ax.plot(d['date'], series.dropna(), color=color, linewidth=2.5, zorder=4)
    ax.fill_between(d['date'], series.dropna(), color=color, alpha=0.12,
                    linewidth=0, zorder=2)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(0, y_max)
    style_axes(fig, ax, d['date'])
    png, svg = save_chart(fig, filename, out_dir)
    plt.close(fig)
    print(png)


def bar_chart(series, color, y_ticks, y_labels, y_max, out_dir, filename):
    d = df[series.notna()]
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=150)
    ax.vlines(d['date'], 0, series.dropna(), color=color, linewidth=0.8 * 229 / len(d),  # 229일 기준 두께, 일수 비례
              capstyle='butt')
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(0, y_max)
    style_axes(fig, ax, d['date'])
    png, svg = save_chart(fig, filename, out_dir)
    plt.close(fig)
    print(png)


# Curvance TVL (피크 $141.3M)
line_area_chart(df['tvl_excluding_borrowed_usd'] / 1e6, COLOR_TVL,
                [0, 40, 80, 120, 160], ['$0M', '$40M', '$80M', '$120M', '$160M'],
                160, 'outputs/charts/curvance/tvl', 'curvance_tvl_tall')

# Curvance 차입금 (피크 $88.1M)
line_area_chart(df['borrowed_usd'] / 1e6, COLOR_BORROWS,
                [0, 25, 50, 75, 100], ['$0M', '$25M', '$50M', '$75M', '$100M'],
                100, 'outputs/charts/curvance/borrows', 'curvance_borrows_tall')

# Curvance 일일 수수료 (피크 $23.4K)
bar_chart(df['fees_usd'] / 1e3, COLOR_FEES,
          [0, 10, 20, 30], ['$0K', '$10K', '$20K', '$30K'],
          30, 'outputs/charts/curvance/fees', 'curvance_daily_fees_tall')
