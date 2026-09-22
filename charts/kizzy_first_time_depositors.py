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
df = pd.read_csv('sources/figure17_kizzy_first_time_depositors.csv',
                 parse_dates=['date'])

COLOR_FTD = '#2563EB'   # 딥 블루 (일별 FTD 바)
COLOR_CUM = '#7C3AED'   # 바이올렛 (누적 FTD 라인)

# =============================================================================
# Chart: 일별 FTD 바 (좌축) + 누적 FTD 라인 (우축)
# =============================================================================
fig, ax = create_figure('bar')

ax.vlines(df['date'], 0, df['first_time_depositors'], color=COLOR_FTD,
          linewidth=1.6, capstyle='butt', zorder=3)

# 좌축: 일별 FTD (피크 177)
ax.set_yticks([0, 50, 100, 150])
ax.set_ylim(0, 185)

# 우축: 누적 FTD (최종 1,487), 좌축과 동일 비율로 틱 정렬
ax2 = ax.twinx()
ax2.plot(df['date'], df['cumulative_ftd'], color=COLOR_CUM, linewidth=2.5,
         zorder=4)
ax2.set_yticks([0, 500, 1000, 1500])
ax2.set_yticklabels(['0', '500', '1,000', '1,500'])
ax2.set_ylim(0, 1850)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[12, 2, 4, 6]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min() - pd.Timedelta(days=1),
            df['date'].max() + pd.Timedelta(days=1))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

# 우축 스타일 (apply_style은 주축만 처리)
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=16, pad=15, length=0, colors='#787b86')
ax2.set_facecolor('none')

fig.tight_layout()
png, svg = save_chart(fig, 'kizzy_first_time_depositors',
                      'outputs/charts/kizzy/metrics')
plt.close(fig)
print(png)
