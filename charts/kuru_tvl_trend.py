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
df = pd.read_csv('sources/figure03_kuru_tvl.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})
df['tvl_m'] = df['tvl_usd'] / 1e6

COLOR_KURU = '#9FE870'  # Kuru 라임 그린

# =============================================================================
# Chart: TVL line + light area fill (레퍼런스 동일 구성)
# =============================================================================
fig, ax = create_figure('area')

ax.plot(df['date'], df['tvl_m'], color=COLOR_KURU, linewidth=2.5, zorder=4)
ax.fill_between(df['date'], df['tvl_m'], color=COLOR_KURU, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0M~$2.0M, $0.5M 간격 (5 ticks, 피크 $2.15M은 상단 여백에 수용)
y_ticks = [0, 0.5, 1.0, 1.5, 2.0]
ax.set_yticks(y_ticks)
ax.set_yticklabels(['$0M', '$0.5M', '$1.0M', '$1.5M', '$2.0M'])
ax.set_ylim(0, 2.3)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 4, 6, 8]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'kuru_tvl_trend', 'outputs/charts/kuru/tvl')
plt.close(fig)
print(png)
