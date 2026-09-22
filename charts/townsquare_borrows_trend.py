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
df = pd.read_csv('sources/figure12_townsquare_borrows.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})
d = df[df['borrowed_usd'].notna()]
borrows_m = d['borrowed_usd'] / 1e6

COLOR_TOWNSQUARE = '#8B5CF6'  # 바이올렛

# =============================================================================
# Chart: 차입금 line + light area fill
# =============================================================================
fig, ax = create_figure('area')

ax.plot(d['date'], borrows_m, color=COLOR_TOWNSQUARE, linewidth=2.5, zorder=4)
ax.fill_between(d['date'], borrows_m, color=COLOR_TOWNSQUARE, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0M~$3M, $1M 간격 (피크 $2.66M)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(['$0M', '$1M', '$2M', '$3M'])
ax.set_ylim(0, 3)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 3, 5, 7, 9]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(d['date'].min(), d['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'townsquare_borrows_trend',
                      'outputs/charts/townsquare/borrows')
plt.close(fig)
print(png)
