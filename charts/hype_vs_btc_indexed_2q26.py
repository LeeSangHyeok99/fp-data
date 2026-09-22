import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from pathlib import Path
import json
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

BASE_DATE = '2026-03-31'   # 지수 기준일 (2Q26 시작 직전 종가)
END_DATE = '2026-06-30'    # 분기말

# HYPE 일별 종가 (ASXN)
h = pd.DataFrame(json.load(open('sources/hyperliquid-q2-data/asxn/raw/HYPE_PRICE.json')))
h['date'] = pd.to_datetime(h['date'])
hype = h.set_index('date')['close']

# BTC perp 일별 종가 (Hyperliquid API 1d 캔들)
b = pd.DataFrame(json.load(
    open('sources/hyperliquid-q2-data/external/raw/hlapi_btc_1d_candles.json')))
b['date'] = pd.to_datetime(b['t'], unit='ms')
btc = b.set_index('date')['c'].astype(float)

hype_i = hype[BASE_DATE:END_DATE] / hype.loc[BASE_DATE] * 100
btc_i = btc[BASE_DATE:END_DATE] / btc.loc[BASE_DATE] * 100

MINT = '#50e3c2'    # HYPE
PURPLE = '#8b6fd4'  # BTC
TEXT = '#111111'
TICK = '#747474'
FS_Y, FS_X = 8, 7  # 800px 폭 차트 공통 축 폰트 크기

setup_font()
# 800 x 390 @150dpi. bbox_inches='tight'는 크기를 줄이므로 저장 시 미사용
fig, ax = plt.subplots(figsize=(5.333, 2.6), dpi=DPI)

# 기준선 100
ax.axhline(100, color=TICK, linewidth=0.8, alpha=0.5, zorder=1)

ax.plot(hype_i.index, hype_i.values, color=MINT, linewidth=1.5, zorder=3)
ax.plot(btc_i.index, btc_i.values, color=PURPLE, linewidth=1.5, zorder=2)

for series, color in [(hype_i, MINT), (btc_i, PURPLE)]:
    ax.text(series.index[-1] + pd.Timedelta(days=2), series.iloc[-1],
            f'{series.iloc[-1] - 100:+.0f}%', ha='left', va='center',
            fontsize=8, fontweight='bold', color=color)

ax.set_ylim(82, 212)
ax.set_yticks([100, 150, 200])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}'))

months = pd.date_range('2026-04-01', END_DATE, freq='MS')
ax.set_xticks(months)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
# 오른쪽에 라벨 자리 확보
ax.set_xlim(hype_i.index[0], hype_i.index[-1] + pd.Timedelta(days=13))

apply_style(fig, ax, 'line')

ax.tick_params(axis='y', labelsize=FS_Y, length=0, colors=TICK, pad=5)
ax.tick_params(axis='x', labelsize=FS_X, colors=TICK, pad=4, length=4, width=1)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=0.7)
ax.set_axisbelow(True)

# apply_style의 tight_layout은 기본 폰트(16~18pt) 기준이라 여백이 남는다. 축소 폰트로 재계산
fig.tight_layout()

output_dir = 'outputs/charts/hyperliquid/token'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'hype_vs_btc_indexed_2q26'

pd.DataFrame({'HYPE': hype_i, 'BTC': btc_i}).round(2).to_csv(f'outputs/data/{name}.csv')
fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
