import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, endpoint_dot, save_chart, setup_font

# =============================================================================
# Data: DefiLlama 월별 거래량 (perps 페이지 chartData + /overview/dexs)
# =============================================================================
df = pd.read_csv('outputs/data/perp_vs_spot_dex_monthly.csv', parse_dates=['month'])
df = df[df['month'] >= '2025-01-01'].reset_index(drop=True)

COLOR_PERP = '#5470C6'  # 블루
COLOR_SPOT = '#EE6666'  # 레드

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

for col, color in [('spot_volume_usd', COLOR_SPOT), ('perp_volume_usd', COLOR_PERP)]:
    v = df[col] / 1e9
    ax.plot(df['month'], v, color=color, linewidth=2.4, zorder=3)
    endpoint_dot(ax, df['month'].iloc[-1], v.iloc[-1], color=color)

ax.set_yticks([0, 400, 800, 1200])
ax.set_yticklabels(['$0B', '$400B', '$800B', '$1,200B'])
ax.set_ylim(0, 1430)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['month'].min(), df['month'].max())

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=12)

print(save_chart(fig, 'perp_vs_spot_dex_volume', 'outputs/charts/dex/volume')[0])
