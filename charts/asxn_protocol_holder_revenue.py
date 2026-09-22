import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

# 그라데이션 바는 four-pillars에만 있다. 모듈명이 'config'로 겹쳐 경로 지정 로드
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'fp_config', '.claude/skills/design/four-pillars/config.py')
_fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fp)
gradient_rounded_bar = _fp.gradient_rounded_bar

mpl.rcParams['axes.unicode_minus'] = False

# --light: 흰 배경용 (800px 폭). 기본: 1600px
LIGHT = '--light' in sys.argv

df = pd.read_csv('outputs/data/asxn_protocol_holder_revenue.csv')
labels = pd.to_datetime(df['month']).dt.strftime('%b %Y')
x = range(len(df))

MINT = '#50e3c2'                            # protocol revenue (bar)
PURPLE = '#8b6fd4' if LIGHT else '#b9a7e8'  # holder revenue (line)
TEXT = '#111111'                            # 값 라벨: 흰 배경에 얹으므로 검은색
TICK = '#333333' if LIGHT else COLORS['text_secondary']
BAND_ALPHA = 0.16 if LIGHT else 0.08

# 800 x 440 @150dpi (light) / 1600 x 700 (기본)
FIGSIZE = (5.33, 2.93) if LIGHT else (10.67, 4.67)
FS_Y, FS_X, FS_VAL, FS_Q = (9, 8, 8, 10) if LIGHT else (18, 15, 15, 17)

setup_font()
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

ax.plot(x, df['holder_revenue_musd'], color=PURPLE,
        linewidth=1.4 if LIGHT else 2.2,
        marker='o', markersize=4 if LIGHT else 7,
        markeredgecolor='none', zorder=5)

# 2Q26 highlight band (Apr~Jun)
ax.axvspan(5.5, 8.6, color=MINT, alpha=BAND_ALPHA, zorder=0)
ax.text(7.05, 114, '2026 Q2', ha='center', va='bottom',
        fontsize=FS_Q, fontweight='bold', color=PURPLE if LIGHT else MINT)

for xi, v in zip(x, df['protocol_revenue_musd']):
    ax.text(xi, v + 3, f'${v:.0f}M', ha='center', va='bottom',
            fontsize=FS_VAL, fontweight='bold', color=TEXT)

ax.set_ylim(0, 125)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_xlim(-0.7, 8.7)

# 그라데이션 바 (xlim/ylim 확정 후 호출해야 코너 반경이 맞는다)
for xi, v in zip(x, df['protocol_revenue_musd']):
    gradient_rounded_bar(ax, x_center=xi, width=0.62, height=v,
                         color=MINT, floor=0.6, round_top=False)

apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=FS_Y, length=0, colors=TICK,
               pad=6 if LIGHT else 15)
ax.tick_params(axis='x', labelsize=FS_X, colors=TICK,
               pad=4 if LIGHT else 10,
               length=3 if LIGHT else 6, width=0.8 if LIGHT else 1)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=0.7 if LIGHT else GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/hyperliquid/revenue'
Path(output_dir).mkdir(parents=True, exist_ok=True)
name = 'asxn_protocol_holder_revenue' + ('_light' if LIGHT else '')

fig.savefig(f'{output_dir}/{name}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/{name}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)

plt.close(fig)
print(f'PNG: {output_dir}/{name}.png')
