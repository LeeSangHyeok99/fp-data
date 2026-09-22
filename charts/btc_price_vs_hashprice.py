import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    setup_font, save_chart, endpoint_dot, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG,
)

setup_font()

PRICE_COLOR = COLORS['text']   # Bitcoin Price (LHS)
HASH_COLOR = '#fc8452'         # Hashprice (RHS)
BREAKEVEN = (27, 31)           # 레퍼런스의 손익분기 해시프라이스 밴드

df = pd.read_csv('sources/data8_network_daily_2017.csv', parse_dates=['date'])
df = df[df['date'] >= '2025-09-01'].sort_values('date').reset_index(drop=True)

# 일별 톱니를 걷어낸다. 1년 창이라 7일 중심이동평균이면 추세는 그대로 두고
# 고점/저점 시점도 하루 이틀 안에서만 움직인다.
SMOOTH = 7
for col in ('price_usd', 'hashprice_usd_per_ph_day'):
    df[col] = df[col].rolling(SMOOTH, center=True, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 좌/우 축 눈금 간격을 20K : 10 (=2000배)으로 고정해 양쪽 그리드가 겹치게 한다.
ax_r = ax.twinx()
ax_r.axhspan(*BREAKEVEN, color=HASH_COLOR, alpha=0.14, linewidth=0, zorder=1)
ax_r.plot(df['date'], df['hashprice_usd_per_ph_day'],
          color=HASH_COLOR, linewidth=1.6, zorder=4)
ax_r.set_ylim(18, 66)
ax_r.set_yticks([20, 30, 40, 50, 60])
ax_r.set_yticklabels([f'${v}' for v in (20, 30, 40, 50, 60)], fontweight='bold')

ax.plot(df['date'], df['price_usd'], color=PRICE_COLOR, linewidth=1.6, zorder=6)
ax.set_zorder(2)
ax.patch.set_visible(False)
ax.set_ylim(36000, 132000)
ax.set_yticks([40000, 60000, 80000, 100000, 120000])
ax.set_yticklabels([f'${v // 1000}K' for v in (40000, 60000, 80000, 100000, 120000)],
                   fontweight='bold')

ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x',
               labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6,
               colors=COLORS['text_secondary'],
               length=AXIS_CONFIG['x_tick']['length'],
               width=AXIS_CONFIG['x_tick']['width'],
               pad=AXIS_CONFIG['x_tick']['pad'])
for label in ax.xaxis.get_majorticklabels():
    label.set_fontweight('bold')
    label.set_rotation(AXIS_CONFIG['x_tick']['rotation'])
    label.set_ha(AXIS_CONFIG['x_tick']['ha'])

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for a in (ax, ax_r):
    for spine in a.spines.values():
        spine.set_visible(False)
    a.margins(x=0)
ax.tick_params(axis='y', length=0, colors=PRICE_COLOR,
               labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6,
               pad=AXIS_CONFIG['y_tick']['pad'])
ax_r.tick_params(axis='y', length=0, colors=HASH_COLOR,
                 labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6,
                 pad=AXIS_CONFIG['y_tick']['pad'])

# --- 주석 (레퍼런스와 동일 지점) ---
peak = df.loc[df['price_usd'].idxmax()]
trough = df.loc[df['price_usd'].idxmin()]
hp_low = df.loc[df['hashprice_usd_per_ph_day'].idxmin()]
last = df.iloc[-1]
ANN = dict(fontsize=12, fontweight='bold', zorder=7, parse_math=False)

ax.scatter([peak['date']], [peak['price_usd']], s=34, color=PRICE_COLOR,
           zorder=7, edgecolors='none')
ax.annotate(f"{peak['date']:%b %-d, %Y}\n${peak['price_usd']:,.0f}",
            xy=(peak['date'], peak['price_usd']),
            xytext=(20, 2), textcoords='offset points',
            ha='left', va='top', color=PRICE_COLOR, **ANN)

ax.scatter([trough['date']], [trough['price_usd']], s=34, color=PRICE_COLOR,
           zorder=7, edgecolors='none')
ax.annotate(f"{trough['date']:%b %-d, %Y}\n${trough['price_usd']:,.0f}",
            xy=(trough['date'], trough['price_usd']),
            xytext=(-56, -10), textcoords='offset points',
            ha='right', va='top', color=PRICE_COLOR, **ANN)

ax_r.scatter([hp_low['date']], [hp_low['hashprice_usd_per_ph_day']], s=34,
             color=HASH_COLOR, zorder=7, edgecolors='none')
ax_r.annotate(f"Hashprice Low ${hp_low['hashprice_usd_per_ph_day']:.1f}\n({hp_low['date']:%b %-d, %Y})",
              xy=(hp_low['date'], hp_low['hashprice_usd_per_ph_day']),
              xytext=(22, -34), textcoords='offset points',
              ha='left', va='top', color=HASH_COLOR,
              arrowprops=dict(arrowstyle='-', color=HASH_COLOR, linewidth=1.2,
                              shrinkA=2, shrinkB=4), **ANN)

endpoint_dot(ax_r, last['date'], last['hashprice_usd_per_ph_day'],
             color=HASH_COLOR, size=34)
ax_r.annotate(f"{last['date']:%b %-d, %Y}\n${last['hashprice_usd_per_ph_day']:.1f}",
              xy=(last['date'], last['hashprice_usd_per_ph_day']),
              xytext=(-8, 46), textcoords='offset points',
              ha='right', va='bottom', color=HASH_COLOR,
              arrowprops=dict(arrowstyle='-', color=HASH_COLOR, linewidth=1.2,
                              shrinkA=4, shrinkB=4), **ANN)

ax_r.annotate('Breakeven Hashprice Range\n($27 To $31/PH/Day)',
              xy=(df['date'].iloc[6], BREAKEVEN[1] - 0.6),
              ha='left', va='top', color=HASH_COLOR, **ANN)

fig.tight_layout()
print(save_chart(fig, 'btc_price_vs_hashprice',
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
