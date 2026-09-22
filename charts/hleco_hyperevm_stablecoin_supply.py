import json
import sys
import importlib.util
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
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

SRC = 'sources/hyperliquid-q2-data/asxn/raw/HYPER_EVM_STABLECOIN_SUPPLY_CHART__all.json'
rows = [{'date': r['date'], 'coin': s['stablecoin'], 'supply': s['supply']}
        for r in json.load(open(SRC))['chart_data'] for s in r['stablecoins']]
raw = pd.DataFrame(rows)
raw['date'] = pd.to_datetime(raw['date'])

# 월말 스냅샷, 2025년 10월 ~ 2026년 6월
piv = raw.pivot_table(index='date', columns='coin', values='supply', aggfunc='sum')
me = piv.resample('ME').last()['2025-10-01':'2026-06-30'] / 1e9

NAMED = ['USDC', 'USDT0', 'USDH']
df = me[NAMED].copy()
df['Other'] = me.drop(columns=NAMED).sum(axis=1)
labels = df.index.strftime('%b %Y')
totals = df.sum(axis=1).values
x = range(len(df))

COLORS = {'USDC': '#50e3c2', 'USDT0': '#b9a7e8', 'USDH': '#6c63d6', 'Other': '#4dbfc9'}
TEXT = '#ffffff'
TICK = '#747474'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 6.4)
ax.set_yticks([0, 2, 4, 6])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_xlim(-0.7, len(df) - 0.3)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=20, length=0, colors=TICK, pad=12)
ax.tick_params(axis='x', labelsize=18, length=6, width=1, pad=8, rotation=45,
               colors=TICK)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
fig.canvas.draw()  # gradient_rounded_bar가 픽셀 변환을 쓰므로 축 확정 후 그린다

# 그라데이션 스택. 세그먼트마다 자기 구간(y0~y1)에만 그라데이션을 준다
STACK = ['USDC', 'USDT0', 'USDH', 'Other']
cum = df[STACK].cumsum(axis=1)
for i, col in enumerate(STACK):
    lower = cum[STACK[i - 1]].values if i else [0] * len(df)
    for xi, y0, y1 in zip(x, lower, cum[col].values):
        # 위쪽 밴드는 구간이 얇아 그라데이션 폭이 넓으면 딱딱 갈라져 보인다
        gradient_rounded_bar(ax, x_center=xi, width=0.62, height=y1, y0=y0,
                             color=COLORS[col], floor=0.6 if i == 0 else 0.85,
                             round_top=False)

for xi, v in zip(x, totals):
    ax.text(xi, v + 0.12, f'${v:.1f}B', ha='center', va='bottom',
            fontsize=16, fontweight='bold', color=TEXT, zorder=4)

ax.axhline(0, color=TICK, alpha=0.6, linewidth=1, zorder=4)

out = 'outputs/charts/hyperliquid/stablecoin'
Path(out).mkdir(parents=True, exist_ok=True)
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_hyperevm_stablecoin_supply.{ext}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(df.round(3).assign(Total=totals.round(2)).to_string())
print('USDC share Jun 2026: %.1f%%' % (df['USDC'].iloc[-1] / totals[-1] * 100))
