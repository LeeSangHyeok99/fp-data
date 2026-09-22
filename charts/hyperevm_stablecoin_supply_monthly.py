import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
import json
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

# 그라데이션 바는 four-pillars에만 있다. 모듈명이 'config'로 겹쳐 경로 지정 로드
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'fp_config', '.claude/skills/design/four-pillars/config.py')
_fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fp)
gradient_rounded_bar = _fp.gradient_rounded_bar

mpl.rcParams['axes.unicode_minus'] = False

SRC = 'sources/hyperliquid-q2-data/asxn/raw/HYPER_EVM_STABLECOIN_SUPPLY_CHART__all.json'
rows = []
for r in json.load(open(SRC))['chart_data']:
    for s in r['stablecoins']:
        rows.append({'date': r['date'], 'coin': s['stablecoin'], 'supply': s['supply']})
raw = pd.DataFrame(rows)
raw['date'] = pd.to_datetime(raw['date'])

# 월말 스냅샷, 2025년 10월 ~ 2026년 6월
piv = raw.pivot_table(index='date', columns='coin', values='supply', aggfunc='sum')
me = piv.resample('ME').last()['2025-10-01':'2026-06-30'] / 1e9

NAMED = ['USDC', 'USDT0', 'USDH']
df = me[NAMED].copy()
df['Other'] = me.drop(columns=NAMED).sum(axis=1)
labels = df.index.strftime('%b %Y')
x = range(len(df))

COLORS = {'USDC': '#50e3c2', 'USDT0': '#b9a7e8', 'USDH': '#6c63d6', 'Other': '#4dbfc9'}
TEXT = '#111111'
TICK = '#747474'
FS_Y, FS_X = 8, 7  # 800px 폭 차트 공통 축 폰트 크기

setup_font()
# 800 x 390 @150dpi. bbox_inches='tight'는 크기를 줄이므로 저장 시 미사용
fig, ax = plt.subplots(figsize=(5.333, 2.6), dpi=DPI)

totals = df.sum(axis=1).values

ax.set_ylim(0, 6.4)
ax.set_yticks([0, 2, 4, 6])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))

ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_xlim(-0.7, len(df) - 0.3)

# 그라데이션 스택 (xlim/ylim 확정 후). 각 세그먼트는 0부터만 그려지므로
# 누적합이 큰 순서로 겹쳐 그려서 위쪽 밴드가 아래 밴드를 덮게 한다
STACK = ['USDC', 'USDT0', 'USDH', 'Other']
for i in range(len(STACK) - 1, -1, -1):
    col = STACK[i]
    cum = df[STACK[:i + 1]].sum(axis=1).values
    for xi, h in zip(x, cum):
        gradient_rounded_bar(ax, x_center=xi, width=0.62, height=h,
                             color=COLORS[col], floor=0.6, round_top=False)

for xi, v in zip(x, totals):
    ax.text(xi, v + 0.12, f'${v:.1f}B', ha='center', va='bottom',
            fontsize=7, fontweight='bold', color=TEXT, zorder=4)

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=FS_Y, length=0, colors=TICK, pad=5)
ax.tick_params(axis='x', labelsize=FS_X, colors=TICK, pad=4, length=4, width=1)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=0.7)
ax.set_axisbelow(True)

# apply_style의 tight_layout은 기본 폰트(16~18pt) 기준이라 여백이 남는다. 축소 폰트로 재계산
fig.tight_layout()

output_dir = 'outputs/charts/hyperliquid/stablecoin'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'hyperevm_stablecoin_supply_monthly'

df.round(4).to_csv(f'outputs/data/{name}.csv')
fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
