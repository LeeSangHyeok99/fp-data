import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    setup_font, save_chart, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG,
)

setup_font()

# 모드 (인자로 선택)
#   기본    : 좌 선형 USD + 우 로그 공유축(난이도/해시프라이스). 축 라벨 2개.
#   dual    : 선형. 해시프라이스에 전용 우축을 더 붙인다. 축 라벨 3개.
#   index   : 좌축은 USD 가격 그대로, 우축 두 시리즈(난이도/해시프라이스)만 각자
#             기준값으로 지수화해 우축 하나로 합친다. 축 라벨 2개.
MODE = next((a for a in sys.argv[1:] if a in ('dual', 'index')), 'log')
LOG = MODE == 'log'
# index 모드에 'log'를 같이 주면 우측 지수 축을 로그로 그린다. 해시프라이스 자체
# 변동폭이 143배라 선형 지수 축에서는 2020년 이후가 바닥에 눕는다.
INDEX_LOG = MODE == 'index' and 'log' in sys.argv[1:]

# index 모드 기준값. 두 시리즈가 모두 0~200 안에 들어오도록 잡은 값이라
# 반드시 노트에 병기해야 한다 (기준값 없이는 선 사이 위아래 관계가 의미 없다).
INDEX_BASE = {'difficulty_t': 80, 'hashprice_usd_per_ph_day': 2000}

# 축 틱은 공용 config 기본값보다 6pt 작게 (이 차트만)
XT = AXIS_CONFIG['x_tick']['fontsize'] - 6
YT = AXIS_CONFIG['y_tick']['fontsize'] - 6

PRICE_COLOR = '#fac858'   # Bitcoin Price (USD)
DIFF_COLOR = '#fc8452'    # Network Difficulty (T)
HASH_COLOR = '#73c0de'    # Hashprice (USD/PH/Day)

df = pd.read_csv('sources/data8_network_daily_2017.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

# 가격/해시프라이스는 일별 노이즈(특히 수수료 변동)가 커서 30일 중심이동평균으로 편다.
SMOOTH = 30
for col in ('price_usd', 'hashprice_usd_per_ph_day'):
    df[col] = df[col].rolling(SMOOTH, center=True, min_periods=1).mean()

# 난이도는 2주마다 조정되는 계단이라 그 주기(14일)만 밀어 계단만 없앤다.
df['difficulty_t'] = df['difficulty_t'].rolling(14, center=True, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

if MODE == 'index':
    # 좌축은 USD 가격 그대로. 우축 하나를 지수화한 난이도/해시프라이스가 공유한다.
    idx = {c: df[c] / b * 100 for c, b in INDEX_BASE.items()}
    ax_h = ax_r = ax.twinx()
    ax_r.fill_between(df['date'], idx['hashprice_usd_per_ph_day'], 0,
                      color=HASH_COLOR, alpha=0.12, linewidth=0, zorder=2)
    ax_r.plot(df['date'], idx['hashprice_usd_per_ph_day'],
              color=HASH_COLOR, linewidth=1.5, zorder=4)
    ax_r.plot(df['date'], idx['difficulty_t'], color=DIFF_COLOR, linewidth=1.5, zorder=5)
    if INDEX_LOG:
        ax_r.set_yscale('log')
        ax_r.set_ylim(0.1, 1000)
        ax_r.set_yticks([0.1, 1, 10, 100, 1000])
        ax_r.set_yticklabels(['0.1', '1', '10', '100', '1,000'], fontweight='bold')
        ax_r.minorticks_off()
    else:
        # 좌축 0~128K / 5틱과 같은 비율로 나눠 그리드가 1:1로 대응한다.
        ax_r.set_ylim(0, 128000 / 120000 * 200)
        ax_r.set_yticks([0, 50, 100, 150, 200])
        ax_r.set_yticklabels(['0', '50', '100', '150', '200'], fontweight='bold')
    ax_r.tick_params(axis='y', colors=COLORS['text_secondary'])

    ax.plot(df['date'], df['price_usd'], color=PRICE_COLOR, linewidth=1.5, zorder=6)
    ax.set_zorder(2)
    ax.patch.set_visible(False)
    ax.set_ylim(0, 128000)
    ax.set_yticks([0, 30000, 60000, 90000, 120000])
    ax.set_yticklabels([f'${v // 1000:,}K' for v in (0, 30000, 60000, 90000, 120000)],
                       fontweight='bold')
    ax.tick_params(axis='y', colors=PRICE_COLOR)

else:
    # 우축 구성.
    #  기본: 난이도와 해시프라이스(USD)가 축 하나를 공유한다.
    #  dual: 39~3,954을 오가는 USD 해시프라이스는 난이도(0.3~156) 축에 얹으면 위가
    #        잘리므로 CSV의 USD 해시프라이스를 전용 축(0~4,000)에 따로 그린다.
    ax_r = ax.twinx()
    ax_r.plot(df['date'], df['difficulty_t'], color=DIFF_COLOR, linewidth=1.5, zorder=5)

    if LOG:
        ax_h = ax_r
        ax_h.plot(df['date'], df['hashprice_usd_per_ph_day'],
                  color=HASH_COLOR, linewidth=1.5, zorder=4)
        # 좌축 $0~150K를 5등분(30K)한 그리드에 로그 한 자릿수(1decade)를 정확히 얹는다.
        # 0.1~10,000이면 난이도(0.32~156)와 해시프라이스(39~3,954)가 모두 들어간다.
        ax_r.set_yscale('log')
        ax_r.set_ylim(0.1, 10000)
        ax_r.set_yticks([0.1, 1, 10, 100, 1000])
        ax_r.set_yticklabels(['0.1', '1', '10', '100', '1,000'], fontweight='bold')
        ax_r.minorticks_off()
        ax_r.tick_params(axis='y', colors=COLORS['text_secondary'])
    else:
        hp = df['hashprice_usd_per_ph_day']
        ax_h = ax.twinx()
        ax_h.spines['right'].set_position(('axes', 1.10))
        ax_h.fill_between(df['date'], hp, 0,
                          color=HASH_COLOR, alpha=0.12, linewidth=0, zorder=2)
        ax_h.plot(df['date'], hp, color=HASH_COLOR, linewidth=1.5, zorder=4)
        # 세 축 모두 좌축 0~128K / 5틱과 같은 비율로 나눠 그리드가 1:1로 대응한다.
        ax_r.set_ylim(0, 128000 / 120000 * 160)
        ax_r.set_yticks([0, 40, 80, 120, 160])
        ax_r.set_yticklabels([f'{v}' for v in (0, 40, 80, 120, 160)], fontweight='bold')
        ax_r.tick_params(axis='y', colors=DIFF_COLOR)
        ax_h.set_ylim(0, 128000 / 120000 * 4000)
        ax_h.set_yticks([0, 1000, 2000, 3000, 4000])
        ax_h.set_yticklabels(['$0', '$1,000', '$2,000', '$3,000', '$4,000'],
                             fontweight='bold')
        ax_h.tick_params(axis='y', colors=HASH_COLOR)

    ax.plot(df['date'], df['price_usd'], color=PRICE_COLOR, linewidth=1.5, zorder=6)
    ax.set_zorder(2)
    ax.patch.set_visible(False)
    ax.set_ylim(0, 150000 if LOG else 128000)
    ax.set_yticks([0, 30000, 60000, 90000, 120000])
    ax.set_yticklabels([f'${v // 1000:,}K' for v in (0, 30000, 60000, 90000, 120000)],
                       fontweight='bold')
    ax.tick_params(axis='y', colors=PRICE_COLOR)

ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x',
               labelsize=XT,
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

for a in (ax, ax_r, ax_h):
    for spine in a.spines.values():
        spine.set_visible(False)
    a.margins(x=0)
ax.tick_params(axis='y', length=0, labelsize=YT,
               pad=AXIS_CONFIG['y_tick']['pad'])
for a in (ax_r, ax_h):
    a.tick_params(axis='y', length=0, labelsize=YT,
                  pad=AXIS_CONFIG['y_tick']['pad'])

fig.tight_layout()
print(save_chart(fig, 'btc_price_difficulty_hashprice'
                 + ('' if LOG else '_' + MODE + ('_log' if INDEX_LOG else '')),
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
