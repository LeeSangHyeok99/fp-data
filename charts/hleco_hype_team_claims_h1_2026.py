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

# 월 베스팅 물량. report_facts.json cum_entitled_7mo(69.44M) / 7개월
ENTITLEMENT = 9.92e6
CSV = 'outputs/data/hleco_hype_team_claims_h1_2026.csv'

if not Path(CSV).exists():
    # 월별 실청구량(HYPE). 2Q 합 1,289,000이 report_facts.json q2_claimed과 일치하고,
    # Dec 청구분을 더하면 cum_claimed_since_cliff(4,548,146)와 맞는다
    pd.DataFrame({
        'month': ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'],
        'claimed': [1206000, 139000, 169000, 333000, 422000, 534000],
    }).to_csv(CSV, index=False)

df = pd.read_csv(CSV)
df['pct'] = df['claimed'] / ENTITLEMENT * 100
labels = pd.to_datetime(df['month']).dt.strftime('%b %Y')
x = range(len(df))

MINT = '#50e3c2'   # 청구분
GHOST = '#8aa6a1'  # 미청구 포함 전체 베스팅분
TEXT = '#ffffff'
TICK = '#747474'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 10.6e6)
ax.set_yticks([0, 5e6, 10e6])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1e6:.0f}M'))
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

for xi in x:
    gradient_rounded_bar(ax, x_center=xi, width=0.62, height=ENTITLEMENT,
                         color=GHOST, floor=0.75, round_top=False)
for xi, v in zip(x, df['claimed']):
    gradient_rounded_bar(ax, x_center=xi, width=0.62, height=v,
                         color=MINT, floor=0.6, round_top=False)

# 라벨은 청구분(민트) 바 바로 위에
texts = [ax.text(xi, v + 0.25e6, f'{v/1000:,.0f}K\n{p:.1f}%', ha='center',
                 va='bottom', fontsize=15, fontweight='bold', color=TEXT, zorder=4,
                 linespacing=1.4)
         for xi, (v, p) in enumerate(zip(df['claimed'], df['pct']))]

ax.axhline(0, color=TICK, alpha=0.6, linewidth=1, zorder=4)

out = 'outputs/charts/hyperliquid/token'
Path(out).mkdir(parents=True, exist_ok=True)


def save(name):
    for ext in ('png', 'svg'):
        fig.savefig(f'{out}/{name}.{ext}', dpi=DPI, facecolor='none',
                    edgecolor='none', bbox_inches='tight', transparent=True)


save('hleco_hype_team_claims_h1_2026')

# 정렬 버전: 라벨을 전부 첫 막대 라벨 높이에 맞춘다
for t in texts:
    t.set_y(df['claimed'][0] + 0.25e6)
save('hleco_hype_team_claims_h1_2026_aligned')

plt.close(fig)
print(df.assign(pct=df['pct'].round(1)).to_string(index=False))
print(f'2Q26 합계 {df["claimed"][3:].sum():,} (report_facts q2_claimed=1,289,000)')
print(f'H1 청구율 {df["claimed"].sum()/(ENTITLEMENT*6)*100:.1f}%')
