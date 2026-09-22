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
df = pd.read_csv('sources/figure14_apriori_tvl.csv', parse_dates=['date_utc']).rename(columns={'date_utc': 'date'})
d = df[df['tvl_usd'].notna()]
tvl_m = d['tvl_usd'] / 1e6

COLOR_APRIORI = '#8057F5'  # aPriori 브랜드 바이올렛

# =============================================================================
# Chart: TVL line + light area fill
# =============================================================================
fig, ax = create_figure('area')

ax.plot(d['date'], tvl_m, color=COLOR_APRIORI, linewidth=2.5, zorder=4)
ax.fill_between(d['date'], tvl_m, color=COLOR_APRIORI, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0M~$1M, $0.25M 간격 (범위 $0.51M~$0.85M)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['$0M', '$0.25M', '$0.5M', '$0.75M', '$1M'])
ax.set_ylim(0, 1.0)

# X axis (약 2개월 범위, 월초 2개 틱)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[6, 7, 8, 9]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(d['date'].min(), d['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'apriori_tvl_trend', 'outputs/charts/apriori/tvl')
plt.close(fig)
print(png)
