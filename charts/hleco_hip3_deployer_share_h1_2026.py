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

# 레퍼런스(hl.eco 뉴스레터 차트) 값과 hl.eco 원본 API 값이 1~2월에서 갈린다.
# USE_REFERENCE=True면 레퍼런스 이미지에서 추출한 값을, False면 hl.eco 원본을 쓴다.
USE_REFERENCE = True

if USE_REFERENCE:
    df = pd.read_csv('outputs/data/hleco_hip3_deployer_share_h1_2026_ref.csv',
                     index_col='month')
    # 레퍼런스는 'Jan' ~ 'Jul MTD'로 찍었지만 축 규칙대로 'Mon YYYY'로 표기
    labels = [f"{m.split()[0]} 2026" for m in df.index]
else:
    SRC = ('sources/hyperliquid-q2-data/hleco/raw/'
           'api.hl.eco__api_hrc_markets_hip3-deployers.json')
    series = json.load(open(SRC))['data']['series']
    m = pd.DataFrame({r['period']: r['values'] for r in series
                      if '2026-01' <= r['period'] <= '2026-07'}).T
    m.index = pd.to_datetime(m.index)
    share = m.div(m.sum(axis=1), axis=0) * 100
    # Kinetiq은 1~6월 USDH 북('km')으로 운영하다 6/17 정산 후 7/1부터 USDC 북('mkts')
    # 으로 재출시했다. 두 코드 모두 같은 배포자라 합산한다
    df = pd.DataFrame({
        'trade.xyz': share['xyz'],
        'Dreamcash': share['cash'],
        'Markets by kinetiq': share['km'] + share['mkts'],
        'All others': share.drop(columns=['xyz', 'cash', 'km', 'mkts']).sum(axis=1),
    })
    labels = df.index.strftime('%b %Y').tolist()

x = range(len(df))

COLORS = {'trade.xyz': '#50e3c2', 'Dreamcash': '#b9a7e8',
          'Markets by kinetiq': '#1e5695', 'All others': '#6c63d6'}
TEXT = '#ffffff'
TICK = '#747474'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))
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
STACK = ['trade.xyz', 'Dreamcash', 'Markets by kinetiq', 'All others']
cum = df[STACK].cumsum(axis=1)
for i, col in enumerate(STACK):
    lower = cum[STACK[i - 1]].values if i else [0] * len(df)
    for xi, y0, y1 in zip(x, lower, cum[col].values):
        # 위쪽 밴드는 구간이 얇아 그라데이션 폭이 넓으면 딱딱 갈라져 보인다
        gradient_rounded_bar(ax, x_center=xi, width=0.62, height=y1, y0=y0,
                             color=COLORS[col], floor=0.6 if i == 0 else 0.85,
                             round_top=False)

for xi, v in zip(x, df['trade.xyz']):
    ax.text(xi, 50, f'{v:.0f}%', ha='center', va='center',
            fontsize=17, fontweight='bold', color=TEXT, zorder=4)

ax.axhline(0, color=TICK, alpha=0.6, linewidth=1, zorder=4)

out = 'outputs/charts/hyperliquid/hip3'
Path(out).mkdir(parents=True, exist_ok=True)
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_hip3_deployer_share_h1_2026.{ext}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(df.round(1).to_string())
