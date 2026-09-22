import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
import json
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

SRC = 'sources/hyperliquid-q2-data/asxn/raw/HL_DAILY_UNIQUE_USERS.json'
df = pd.DataFrame(json.load(open(SRC))['chart_data'])
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time')

# 일별 활성 주소를 주간 평균으로. 2025년 1월 ~ 마지막 완전 주 2026-W26(6/28)
df = df[df['time'] <= '2026-06-28']
wk = (df.set_index('time')['daily_unique_users'].resample('W-SUN').mean() / 1000)
wk = wk['2025-01-01':].reset_index()
wk.columns = ['week_end', 'users_k']

MINT = '#50e3c2'  # 2026Q2
BASE = '#8aa6a1'  # 그 외 기간
TICK = '#747474'
FS_Y, FS_X = 8, 7  # 800px 폭 차트 공통 축 폰트 크기

# 2026Q2 시작부터 마지막 주까지 강조 (원본과 동일하게 7월 부분 주차도 포함)
is_q2 = wk['week_end'] >= '2026-04-01'
colors = [MINT if q else BASE for q in is_q2]

setup_font()
# 800 x 390 @150dpi. bbox_inches='tight'는 크기를 줄이므로 저장 시 미사용
fig, ax = plt.subplots(figsize=(5.333, 2.6), dpi=DPI)

x = range(len(wk))
ax.bar(x, wk['users_k'], width=0.8, color=colors, zorder=2)

q2_idx = [i for i, q in enumerate(is_q2) if q]
ax.text(sum(q2_idx) / len(q2_idx), 71, '2026 Q2', ha='center', va='bottom',
        fontsize=9, fontweight='bold', color=MINT)

ax.set_ylim(0, 78)
ax.set_yticks([0, 20, 40, 60])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}K'))

# 13주 간격 ISO 주차 라벨 + 마지막 주(6/30 마감) 라벨
tick_pos = list(range(0, len(wk), 13))
if len(wk) - 1 - tick_pos[-1] >= 4:  # 직전 틱과 겹치지 않을 때만
    tick_pos.append(len(wk) - 1)
ax.set_xticks(tick_pos)
ax.set_xticklabels([wk['week_end'].iloc[i].strftime('%G-W%V') for i in tick_pos])
ax.set_xlim(-1, len(wk))

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=FS_Y, length=0, colors=TICK, pad=5)
ax.tick_params(axis='x', labelsize=FS_X, colors=TICK, pad=4, length=4, width=1)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=0.7)
ax.set_axisbelow(True)

# apply_style의 tight_layout은 기본 폰트(16~18pt) 기준이라 여백이 남는다. 축소 폰트로 재계산
fig.tight_layout()

output_dir = 'outputs/charts/hyperliquid/metrics'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'asxn_perp_active_users_weekly'

wk.to_csv(f'outputs/data/{name}.csv', index=False)
fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
