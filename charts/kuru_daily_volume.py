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
df = pd.read_csv('sources/figure05_kuru_daily_volume.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})
df['vol_m'] = df['kuru_clob_volume_usd'] / 1e6

COLOR_KURU = '#9FE870'  # Kuru 라임 그린

# =============================================================================
# Chart: daily volume bars
# =============================================================================
fig, ax = create_figure('bar')

# bar 대신 vlines: 포인트 단위 두께라 모든 막대가 동일 픽셀 폭으로 렌더됨
# (bar는 날짜→픽셀 반올림 때문에 폭이 3~4px로 들쭉날쭉해져 줄무늬가 생김)
ax.vlines(df['date'], 0, df['vol_m'], color=COLOR_KURU,
          linewidth=2.4 * 229 / len(df), capstyle='butt')

# Y axis: $0M~$450M, $150M 간격 (4 ticks, 9/7 피크 $450M)
y_ticks = [0, 150, 300, 450]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}M' for v in y_ticks])
ax.set_ylim(0, 460)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[12, 2, 4, 6, 8]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
            df['date'].max() + pd.Timedelta(days=1))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'kuru_daily_volume', 'outputs/charts/kuru/volume')
plt.close(fig)
print(png)
