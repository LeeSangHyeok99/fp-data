"""
Bitcoin price vs. network hashrate, Sep 2025 to Sep 2026 (four-pillars dual axis).
가격: sources/data8_network_daily_2017.csv
해시레이트: outputs/data/btc_hashrate_daily_blockchain.csv
  (Blockchain.com charts API의 일별 추정 해시레이트, TH/s를 EH/s로 환산해 저장.
   소스에 결측일이 있어서 2025-11-13~15, 2026-08-17~23은 선형 보간했다. 보간 없이
   계산하면 8월 30일 기준 30일 평균이 924가 아니라 911로 잡힌다.)
  curl "https://api.blockchain.info/charts/hash-rate?timespan=2years&format=json&sampled=false"
"""

import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG

setup_font()

PRICE_COLOR = '#e78034'   # Bitcoin Price (LHS)
HR7_COLOR = '#4e8f83'     # Hashrate 7-Day Avg (RHS)
HR30_COLOR = '#2fb98a'    # Hashrate 30-Day Avg (RHS)
# 인자 없이 실행하면 API 해시레이트, 'csv'를 주면 CSV 난이도 환산본으로 그린다.
CSV_ONLY = 'csv' in sys.argv[1:]
NAME = 'btc_price_vs_network_hashrate' + ('_from_difficulty' if CSV_ONLY else '')

df = pd.read_csv('sources/data8_network_daily_2017.csv', parse_dates=['date'])
if CSV_ONLY:
    # 난이도는 약 2주마다 갱신되므로 7일 평균선이 계단형으로 나온다.
    df['hr7'] = (df['difficulty_t'] * (2 ** 32 / 600 / 1e6)).rolling(7).mean()
    df['hr30'] = (df['difficulty_t'] * (2 ** 32 / 600 / 1e6)).rolling(30).mean()
else:
    hr = pd.read_csv('outputs/data/btc_hashrate_daily_blockchain.csv',
                     parse_dates=['date'])
    # 얇은 선은 일별 추정치의 톱니가 심해 중심 7일 평균을 두 번 걸어(삼각 가중) 눌러
    # 그린다. 위상이 밀리지 않아 굵은 30일선과 봉우리 위치가 맞는다.
    hr['ma7c'] = (hr['hr'].rolling(7, center=True, min_periods=4).mean()
                          .rolling(7, center=True, min_periods=4).mean())
    df = df.merge(hr[['date', 'ma7c', 'ma30']], on='date', how='inner')
    df = df.rename(columns={'ma7c': 'hr7', 'ma30': 'hr30'})
df = df[df['date'] >= '2025-09-01'].sort_values('date').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12.4, 5.4), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 좌/우 눈금 간격을 20K : 100 EH/s (=200배)로 고정해 양쪽 그리드가 겹치게 한다.
ax_r = ax.twinx()
ax_r.axhline(1000, color=HR30_COLOR, linewidth=1.0, alpha=0.55,
             linestyle=(0, (5, 3)), zorder=3)
ax_r.plot(df['date'], df['hr7'], color=HR7_COLOR, linewidth=1.1, zorder=4)
ax_r.plot(df['date'], df['hr30'], color=HR30_COLOR, linewidth=2.2, zorder=5)
ax_r.set_ylim(740, 1240)
ax_r.set_yticks([800, 900, 1000, 1100, 1200])
ax_r.set_yticklabels([f'{v:,}' for v in (800, 900, 1000, 1100, 1200)],
                     fontweight='bold')

ax.plot(df['date'], df['price_usd'], color=PRICE_COLOR, linewidth=1.6, zorder=6)
ax.set_zorder(2)
ax.patch.set_visible(False)
ax.set_ylim(28000, 128000)
ax.set_yticks([40000, 60000, 80000, 100000, 120000])
ax.set_yticklabels([f'${v // 1000}K' for v in (40000, 60000, 80000, 100000, 120000)],
                   fontweight='bold')

ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6,
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
ax_r.tick_params(axis='y', length=0, colors=HR30_COLOR,
                 labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6,
                 pad=AXIS_CONFIG['y_tick']['pad'])

# --- 주석 ---
ANN = dict(fontsize=12, fontweight='bold', zorder=7, parse_math=False)
peak = df.loc[df['hr30'].idxmax()]
aug0 = df[df['date'] == '2026-08-01'].iloc[0]
aug1 = df[df['date'] == '2026-08-30'].iloc[0]

ax_r.annotate(f"30-Day Average High {peak['hr30']:,.0f} EH/s\n"
              f"({peak['date']:%b %-d, %Y})",
              xy=(peak['date'], peak['hr30']), xytext=(-150, 78),
              textcoords='offset points', ha='left', va='bottom',
              color=HR30_COLOR,
              arrowprops=dict(arrowstyle='-', color=HR30_COLOR, linewidth=1.0,
                              shrinkA=6, shrinkB=4), **ANN)
ax_r.annotate('1,000 EH/s', xy=(df['date'].iloc[14], 1000), xytext=(0, -18),
              textcoords='offset points', ha='left', va='center',
              color=HR30_COLOR, **ANN)
ax.annotate(f"August Rally: Price {aug1['price_usd'] / aug0['price_usd'] - 1:+.1%},\n"
            f"30-Day Average Hashrate "
            f"{aug0['hr30']:,.0f} To {aug1['hr30']:,.0f} EH/s",
            xy=(aug1['date'], aug1['price_usd']), xytext=(-300, -46),
            textcoords='offset points', ha='left', va='top', color=PRICE_COLOR,
            arrowprops=dict(arrowstyle='-', color=PRICE_COLOR, linewidth=1.0,
                            shrinkA=6, shrinkB=6), **ANN)

fig.tight_layout()
print(save_chart(fig, NAME,
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
