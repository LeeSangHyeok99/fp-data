import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, gradient_bars, pixel_grid_figure, save_chart

# =============================================================================
# Data: Blockworks Research, fomo: Net Revenue (visualization 10168)
# =============================================================================
df = pd.read_csv('outputs/data/fomo_net_revenue.csv', parse_dates=['date'])
df = df[df['date'] >= '2025-05-01'].reset_index(drop=True)

COLOR = '#5058A4'      # Blockworks 원본 시리즈 색
DAY_PX, BAR_PX = 3, 2  # 하루 3px, 막대 2px (간격 1px)

fig, ax, geom = pixel_grid_figure(len(df), DAY_PX, ax_h=470)

ax.set_yticks([0, 200_000, 400_000, 600_000])
ax.set_yticklabels(['$0K', '$200K', '$400K', '$600K'])
ax.set_ylim(0, 750_000)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
# 하루가 정확히 DAY_PX가 되도록 양끝을 반나절씩만 띄운다
ax.set_xlim(df['date'].min() - pd.Timedelta(hours=12),
            df['date'].max() + pd.Timedelta(hours=12))

gradient_bars(ax, df['date'], df['net_revenue_usd'], COLOR, DAY_PX, BAR_PX,
              floor=0.7)

apply_style(fig, ax, 'bar')  # tight_layout 포함 → 위치 지정은 그 뒤에
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=12)
ax.set_position(geom)

print(save_chart(fig, 'fomo_net_revenue', 'outputs/charts/fomo/revenue',
                 tight=False)[0])
