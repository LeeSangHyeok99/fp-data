import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
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

ENTITLEMENT_M = 9.92  # 월 베스팅 물량 (M HYPE), report_facts.json cum_entitled_7mo / 7

df = pd.read_csv('outputs/data/hype_team_claim_vs_entitlement.csv')
labels = pd.to_datetime(df['month']).dt.strftime('%b %Y')
df['claimed_m'] = df['claim_rate_pct'] / 100 * ENTITLEMENT_M
x = range(len(df))

MINT = '#50e3c2'   # claimed
GHOST = '#8aa6a1'  # entitlement (미청구 포함 전체). 다른 차트의 BASE 회색과 동일
TEXT = '#111111'
TICK = '#747474'
FS_Y, FS_X = 8, 7  # 800px 폭 차트 공통 축 폰트 크기

setup_font()
# 800 x 390 @150dpi. bbox_inches='tight'는 크기를 줄이므로 저장 시 미사용
fig, ax = plt.subplots(figsize=(5.333, 2.6), dpi=DPI)

ax.set_ylim(0, 11)
ax.set_yticks([0, 5, 10])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}M'))

ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_xlim(-0.7, len(df) - 0.3)

# 그라데이션 바 (xlim/ylim 확정 후 호출해야 코너 반경이 맞는다)
for xi in x:
    gradient_rounded_bar(ax, x_center=xi, width=0.62, height=ENTITLEMENT_M,
                         color=GHOST, floor=0.75, round_top=False)
for xi, v in zip(x, df['claimed_m']):
    gradient_rounded_bar(ax, x_center=xi, width=0.62, height=v,
                         color=MINT, floor=0.6, round_top=False)

for xi, (v, p) in enumerate(zip(df['claimed_m'], df['claim_rate_pct'])):
    ax.text(xi, v + 0.25, f'{p}%', ha='center', va='bottom',
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

output_dir = 'outputs/charts/hyperliquid/token'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'hype_team_claim_vs_entitlement'

fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
