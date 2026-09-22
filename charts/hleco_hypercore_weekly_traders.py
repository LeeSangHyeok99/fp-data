import json
import sys
import importlib.util
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

# 그라데이션 바는 four-pillars에만 있다. 모듈명이 'config'로 겹쳐 경로 지정 로드
_spec = importlib.util.spec_from_file_location(
    'fp_config', '.claude/skills/design/four-pillars/config.py')
_fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fp)
gradient_rounded_bar = _fp.gradient_rounded_bar

mpl.rcParams['axes.unicode_minus'] = False

SRC = 'sources/hyperliquid-q2-data/hleco/streams_decoded/decoded__tt-users.json'
dau = pd.DataFrame(json.load(open(SRC))[0]['payload']['hypercore']['dau'])
dau['date'] = pd.to_datetime(dau['t'], unit='ms')
dau = dau.set_index('date')['v'].sort_index()

# 주(월~일) 평균. 첫 주와 마지막 주는 부분 주라 제외하고 완전한 주만 쓴다
START, END = '2025-06-30', '2026-06-28'
wk = dau[START:END].resample('W-SUN').mean()
wk.index = wk.index - pd.Timedelta(days=6)  # 라벨을 주 시작일(월)로

H1_START = pd.Timestamp('2025-12-29')  # 2026 H1 첫 주 시작일

MINT = '#50e3c2'
TEXT = '#ffffff'
TICK = '#747474'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 93000)
ax.set_yticks([0, 20000, 40000, 60000, 80000])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))

ax.set_xlim(mdates.date2num(wk.index.min() - pd.Timedelta(days=5)),
            mdates.date2num(wk.index.max() + pd.Timedelta(days=5)))
ax.set_xticks(pd.date_range('2025-07-01', '2026-05-01', freq='2MS'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=20, length=0, colors=TICK, pad=12)
ax.tick_params(axis='x', labelsize=18, length=6, width=1, pad=8, rotation=45,
               colors=TICK)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# 2026 H1 구간 음영
ax.axvspan(mdates.date2num(H1_START - pd.Timedelta(days=4)), ax.get_xlim()[1],
           color=MINT, alpha=0.07, zorder=0)
ax.text(mdates.date2num(wk.index.max()), 84000, '2026 H1', color=MINT,
        fontsize=18, fontweight='bold', ha='right', va='center', zorder=5)

fig.canvas.draw()  # gradient_rounded_bar가 픽셀 변환을 쓰므로 축 확정 후 그린다
for ts, v in zip(wk.index, wk.values):
    gradient_rounded_bar(ax, mdates.date2num(ts), 5.2, v, MINT, floor=0.22)

peak = wk.idxmax()
ax.text(mdates.date2num(peak), wk.max() + 1800, f'{wk.max():,.0f}', color=TEXT,
        fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=5)

ax.axhline(0, color=TICK, alpha=0.6, linewidth=1, zorder=4)

out = 'outputs/charts/hyperliquid/metrics'
Path(out).mkdir(parents=True, exist_ok=True)
wk.round(0).rename('avg_daily_traders').to_csv(
    'outputs/data/hleco_hypercore_weekly_traders.csv', index_label='week_start')
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_hypercore_weekly_traders.{ext}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(f'weeks={len(wk)}  peak={wk.max():,.0f} ({peak.date()})  '
      f'H1 2026 daily avg={dau["2026-01-01":"2026-06-30"].mean():,.0f}')
