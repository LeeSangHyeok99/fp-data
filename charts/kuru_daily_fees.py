import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, save_chart

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('sources/figure04_kuru_daily_fees.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})

COLOR_AGG = '#9FE870'   # Kuru 라임 그린

# =============================================================================
# Chart: daily fees bars
# =============================================================================
fig, ax = create_figure('bar')

# bar 대신 vlines: 포인트 단위 두께라 모든 막대가 동일 픽셀 폭으로 렌더됨
# CLOB + Aggregator 합산(combined) 단일 시리즈 — CLOB은 첫날 빼면 $1 미만이라 분리해도 안 보임
ax.vlines(df['date'], 0, df['combined_fees_usd'] / 1e3, color=COLOR_AGG,
          linewidth=2.4 * 229 / len(df), capstyle='butt')

# Y axis: $0K~$20K, $5K 간격 (5 ticks, 첫날 $17.5K 수용)
y_ticks = [0, 5, 10, 15, 20]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}K' for v in y_ticks])
ax.set_ylim(0, 21)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[12, 2, 4, 6, 8]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
            df['date'].max() + pd.Timedelta(days=1))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)
png, svg = save_chart(fig, 'kuru_daily_fees', 'outputs/charts/kuru/fees')
plt.close(fig)
print(png)
