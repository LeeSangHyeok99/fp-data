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
df = pd.read_csv('outputs/data/monad_dex_daily_volume.csv', parse_dates=['date'])

COLOR_MONAD = '#836EF9'  # Monad Purple (레퍼런스와 동일 계열)
COLOR_KURU = '#9FE870'   # Kuru 라임 그린

setup_font()


def make_chart(values_m, y_ticks, filename, color):
    """1:1 비율 일일 거래량 바 차트."""
    fig, ax = plt.subplots(figsize=(7.0, 7.0), dpi=150)

    # bar 대신 vlines: 포인트 단위 두께라 모든 막대가 동일 픽셀 폭으로 렌더됨
    # 229일 기준 1.6pt였던 두께를 일수에 비례해 줄여 막대 사이 간격을 유지
    ax.vlines(df['date'], 0, values_m, color=color,
              linewidth=1.6 * 229 / len(df), capstyle='butt')

    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'${v}M' for v in y_ticks])
    ax.set_ylim(0, y_ticks[-1])

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 4, 6, 8]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
                df['date'].max() + pd.Timedelta(days=1))

    apply_style(fig, ax, 'bar')
    ax.tick_params(axis='y', labelsize=16)
    ax.tick_params(axis='x', labelsize=14)

    png, svg = save_chart(fig, filename, 'outputs/charts/monad/dex')
    plt.close(fig)
    print(png)


# Monad 전체 DEX 일일 거래량 (9/7 $513M 피크)
make_chart(df['total_volume_usd'] / 1e6, [0, 150, 300, 450, 600],
           'monad_dex_daily_volume_sq', COLOR_MONAD)

# Kuru 일일 거래량 (9/7 $450M 피크, Monad와 같은 스케일)
make_chart(df['kuru_volume_usd'] / 1e6, [0, 150, 300, 450, 600],
           'kuru_daily_volume_sq', COLOR_KURU)
