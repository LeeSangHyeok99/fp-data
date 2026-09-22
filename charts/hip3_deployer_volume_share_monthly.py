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

SRC = 'sources/hyperliquid-q2-data/hleco/raw/api.hl.eco__api_hrc_markets_hip3-deployers.json'
series = json.load(open(SRC))['data']['series']

# 원본 차트와 동일한 집계 기간 (Oct 2025 ~ Jul 2026). 8월 MTD는 제외
m = pd.DataFrame({r['period']: r['values'] for r in series if r['period'] <= '2026-07'}).T
m.index = pd.to_datetime(m.index)
share = m.div(m.sum(axis=1), axis=0) * 100

# Kinetiq은 1~6월 USDH 북('km')으로 운영하다 6/17 정산 후 7/1부터 USDC 북('mkts')으로
# 재출시했다. 두 코드 모두 같은 배포자(Markets by kinetiq)라 합산한다
df = pd.DataFrame({
    'trade.xyz': share['xyz'],
    'Dreamcash': share['cash'],
    'Markets by kinetiq': share['km'] + share['mkts'],
    'All others': share.drop(columns=['xyz', 'cash', 'km', 'mkts']).sum(axis=1),
})
labels = df.index.strftime('%b %Y')
x = range(len(df))

COLORS = {'trade.xyz': '#50e3c2', 'Dreamcash': '#b9a7e8',
          'Markets by kinetiq': '#1e5695', 'All others': '#6c63d6'}
TEXT = '#ffffff'
TICK = '#747474'
FS_Y, FS_X = 8, 7  # 800px 폭 차트 공통 축 폰트 크기

setup_font()
# 800 x 390 @150dpi. bbox_inches='tight'는 크기를 줄이므로 저장 시 미사용
fig, ax = plt.subplots(figsize=(5.333, 2.6), dpi=DPI)

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))

ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_xlim(-0.7, len(df) - 0.3)

# 그라데이션 스택 (xlim/ylim 확정 후). 각 세그먼트는 0부터만 그려지므로
# 누적합이 큰 순서로 겹쳐 그려서 위쪽 밴드가 아래 밴드를 덮게 한다
STACK = ['trade.xyz', 'Dreamcash', 'Markets by kinetiq', 'All others']
for i in range(len(STACK) - 1, -1, -1):
    col = STACK[i]
    cum = df[STACK[:i + 1]].sum(axis=1).values
    for xi, h in zip(x, cum):
        gradient_rounded_bar(ax, x_center=xi, width=0.62, height=h,
                             color=COLORS[col], floor=0.6, round_top=False)

for xi, v in zip(x, df['trade.xyz']):
    ax.text(xi, 50, f'{v:.0f}%', ha='center', va='center',
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

output_dir = 'outputs/charts/hyperliquid/hip3'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'hip3_deployer_volume_share_monthly'

df.round(2).to_csv(f'outputs/data/{name}.csv')
fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
