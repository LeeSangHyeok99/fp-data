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
df = pd.read_csv('sources/figure06_perpl_tvl.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})
df['tvl_m'] = df['tvl_usd'] / 1e6

COLOR_PERPL = '#9FE870'  # 라임 그린

# =============================================================================
# Chart: TVL line + light area fill
# =============================================================================
fig, ax = create_figure('area')

ax.plot(df['date'], df['tvl_m'], color=COLOR_PERPL, linewidth=2.5, zorder=4)
ax.fill_between(df['date'], df['tvl_m'], color=COLOR_PERPL, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0M~$8M, $2M 간격 (5 ticks, 8/12 피크 $7.6M 수용)
y_ticks = [0, 2, 4, 6, 8]
ax.set_yticks(y_ticks)
ax.set_yticklabels(['$0M', '$2M', '$4M', '$6M', '$8M'])
ax.set_ylim(0, 8)

# X axis (범위를 데이터 시작~끝에 정확히 맞춰 그리드 점선이 라인 밖으로 안 나가게)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'perpl_tvl_trend', 'outputs/charts/perpl/tvl')
plt.close(fig)
print(png)
