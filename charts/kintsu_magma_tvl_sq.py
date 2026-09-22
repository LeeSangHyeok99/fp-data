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
df = pd.read_csv('sources/figure15_kintsu_magma_tvl.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})

COLOR_KINTSU = '#18F3E6'  # Kintsu 브랜드 아쿠아
COLOR_MAGMA = '#F86E00'   # Magma 브랜드 오렌지

setup_font()


def make_chart(col, color, y_ticks, y_labels, y_max, out_dir, filename):
    """1:1 비율 TVL 라인+필 차트."""
    d = df[df[col].notna()]
    tvl_m = d[col] / 1e6

    fig, ax = plt.subplots(figsize=(7.0, 7.0), dpi=150)
    ax.plot(d['date'], tvl_m, color=color, linewidth=2.5, zorder=4)
    ax.fill_between(d['date'], tvl_m, color=color, alpha=0.12,
                    linewidth=0, zorder=2)

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(0, y_max)

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 4, 6, 8]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(d['date'].min(), d['date'].max())

    apply_style(fig, ax, 'area')
    ax.tick_params(axis='y', labelsize=18)
    ax.tick_params(axis='x', labelsize=18)

    png, svg = save_chart(fig, filename, out_dir)
    plt.close(fig)
    print(png)


# Kintsu TVL (피크 $6.04M)
make_chart('kintsu_tvl_usd', COLOR_KINTSU,
           [0, 2, 4, 6], ['$0M', '$2M', '$4M', '$6M'], 6.2,
           'outputs/charts/kintsu/tvl', 'kintsu_tvl_sq')

# Magma TVL (피크 $2.55M)
make_chart('magma_tvl_usd', COLOR_MAGMA,
           [0, 1, 2], ['$0M', '$1M', '$2M'], 2.6,
           'outputs/charts/magma/tvl', 'magma_tvl_sq')
