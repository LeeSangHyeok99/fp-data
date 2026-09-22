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
df = pd.read_csv('sources/figure16_mudigital_tvl.csv', parse_dates=['date'])
d = df[df['mudigital_tvl_usd'].notna()]
tvl_m = d['mudigital_tvl_usd'] / 1e6

COLOR_MUDIGITAL = '#082D73'  # Mu Digital 브랜드 딥 네이비

# =============================================================================
# Chart: TVL line + light area fill
# =============================================================================
fig, ax = create_figure('area')

ax.plot(d['date'], tvl_m, color=COLOR_MUDIGITAL, linewidth=2.5, zorder=4)
ax.fill_between(d['date'], tvl_m, color=COLOR_MUDIGITAL, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0M~$20M, $5M 간격 (피크 $21.6M이 상단 틱 위로 살짝 솟게)
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels(['$0M', '$5M', '$10M', '$15M', '$20M'])
ax.set_ylim(0, 22)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[12, 2, 4, 6]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(d['date'].min(), d['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'mudigital_tvl_trend', 'outputs/charts/mudigital/tvl')
plt.close(fig)
print(png)
