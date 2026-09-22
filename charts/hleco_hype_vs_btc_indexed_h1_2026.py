import json
import sys
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

BASE, END = '2025-12-31', '2026-06-30'  # 2025년 말 종가 = 100

# HYPE 일별 종가 (ASXN)
h = pd.DataFrame(json.load(open('sources/hyperliquid-q2-data/asxn/raw/HYPE_PRICE.json')))
h['date'] = pd.to_datetime(h['date'])
hype = h.set_index('date')['close']

# BTC perp 일별 종가 (Hyperliquid API 1d 캔들)
b = pd.DataFrame(json.load(
    open('sources/hyperliquid-q2-data/external/raw/hlapi_btc_1d_candles.json')))
b['date'] = pd.to_datetime(b['t'], unit='ms')
btc = b.set_index('date')['c'].astype(float)

hype_i = hype[BASE:END] / hype.loc[BASE] * 100
btc_i = btc[BASE:END] / btc.loc[BASE] * 100

MINT = '#50e3c2'    # HYPE
PURPLE = '#8b6fd4'  # BTC
TICK = '#747474'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 기준선 100
ax.axhline(100, color=TICK, alpha=0.35, linewidth=1, zorder=1)

ax.plot(hype_i.index, hype_i.values, color=MINT, linewidth=2.0, zorder=3)
ax.plot(btc_i.index, btc_i.values, color=PURPLE, linewidth=2.0, zorder=3)
for s_, c in ((hype_i, MINT), (btc_i, PURPLE)):
    ax.scatter(s_.index[-1], s_.iloc[-1], color=c, s=50, zorder=5, edgecolors='none',
                clip_on=False)

ax.set_ylim(55, 325)  # 상단 여백은 끝점 라벨 자리
ax.set_yticks([100, 150, 200, 250, 300])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}'))

ax.set_xlim(hype_i.index[0], hype_i.index[-1])
ax.set_xticks(pd.date_range('2026-01-01', '2026-06-01', freq='MS'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=20, length=0, colors=TICK, pad=12)
ax.tick_params(axis='x', labelsize=18, length=6, width=1, pad=8, rotation=45,
               colors=TICK)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# 틱마크가 허공에 뜨지 않게 하단 축선을 살린다
ax.spines['bottom'].set_visible(True)
ax.spines['bottom'].set_color(TICK)
ax.spines['bottom'].set_alpha(0.6)
ax.spines['bottom'].set_linewidth(1)

# 끝점 라벨. 축 안쪽에 두어 잘리지 않게 한다
ax.text(hype_i.index[-1], 310, f'HYPE +{hype_i.iloc[-1] - 100:.0f}%', color=MINT,
        fontsize=17, fontweight='bold', ha='right', va='center', zorder=5)
ax.text(btc_i.index[-1], btc_i.iloc[-1] + 10, f'BTC ({100 - btc_i.iloc[-1]:.0f})%',
        color=PURPLE, fontsize=17, fontweight='bold', ha='right', va='bottom', zorder=5)

out = 'outputs/charts/hyperliquid/token'
Path(out).mkdir(parents=True, exist_ok=True)
pd.DataFrame({'HYPE': hype_i.round(2), 'BTC': btc_i.round(2)}).to_csv(
    'outputs/data/hype_vs_btc_indexed_h1_2026.csv', index_label='date')
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_hype_vs_btc_indexed_h1_2026.{ext}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(f'HYPE {hype_i.iloc[-1]:.1f} (+{hype_i.iloc[-1]-100:.0f}%)  '
      f'BTC {btc_i.iloc[-1]:.1f} ({100-btc_i.iloc[-1]:.0f})%  peak HYPE {hype_i.max():.1f}')
