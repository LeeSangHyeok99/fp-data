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
df = pd.read_csv('sources/figure08_nadfun_daily_volume_fees.csv',
                 parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})

COLOR_VOLUME = '#816CF9'  # 퍼플
COLOR_FEES = '#DDD7FE'    # 라이트 라벤더

setup_font()


def make_chart(values, color, y_ticks, y_labels, y_max, out_dir, filename):
    """1:1 비율 일일 시리즈 바(vlines) 차트."""
    fig, ax = plt.subplots(figsize=(7.0, 7.0), dpi=150)

    # bar 대신 vlines: 포인트 단위 두께라 모든 막대가 동일 픽셀 폭으로 렌더됨
    ax.vlines(df['date'], 0, values, color=color, linewidth=1.6 * 229 / len(df),  # 229일 기준 두께, 일수 비례
              capstyle='butt')

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(0, y_max)

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 4, 6, 8]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
                df['date'].max() + pd.Timedelta(days=1))

    apply_style(fig, ax, 'bar')
    ax.tick_params(axis='y', labelsize=18)
    ax.tick_params(axis='x', labelsize=15)

    png, svg = save_chart(fig, filename, out_dir)
    plt.close(fig)
    print(png)


# Nad.fun 일일 거래량 (피크 $14.95M)
make_chart(df['dex_volume_usd'] / 1e6, COLOR_VOLUME,
           [0, 5, 10, 15], ['$0M', '$5M', '$10M', '$15M'], 15.3,
           'outputs/charts/nadfun/volume', 'nadfun_daily_volume_sq')

# Nad.fun 일일 수수료 (피크 $245.2K)
make_chart(df['fees_usd'] / 1e3, COLOR_FEES,
           [0, 50, 100, 150, 200],
           ['$0K', '$50K', '$100K', '$150K', '$200K'], 250,
           'outputs/charts/nadfun/fees', 'nadfun_daily_fees_sq')
