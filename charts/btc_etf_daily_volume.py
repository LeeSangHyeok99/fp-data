import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/btc_etf_daily_volume.csv', index_col=0, parse_dates=True)

# Others 묶기 (IBIT, FBTC, GBTC, ARKB 외)
main_etfs = ['IBIT', 'FBTC', 'GBTC', 'ARKB']
df['Others'] = df.drop(columns=main_etfs, errors='ignore').sum(axis=1)
df = df[main_etfs + ['Others']]

# $B 단위로 변환
df = df / 1e9

# =============================================================================
# 브랜드 컬러
# =============================================================================
ETF_COLORS = {
    'IBIT':   '#1a1a2e',   # BlackRock 다크 네이비
    'FBTC':   '#4CAF50',   # Fidelity 그린
    'GBTC':   '#8B8B8B',   # Grayscale 그레이
    'ARKB':   '#FF6B35',   # ARK 오렌지
    'Others': '#5470c6',   # 블루
}

# 스택 순서 (아래에서 위로)
stack_order = ['Others', 'ARKB', 'GBTC', 'FBTC', 'IBIT']

# =============================================================================
# 차트 생성
# =============================================================================
fig, ax = create_figure('stacked_bar')

# 투명 배경
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 정수 인덱스로 변환 (주말 갭 제거)
x_pos = np.arange(len(df))

# Stacked bar
bottom = np.zeros(len(df))
bar_width = 0.8

for etf in stack_order:
    ax.bar(
        x_pos,
        df[etf].values,
        bottom=bottom,
        width=bar_width,
        color=ETF_COLORS[etf],
        edgecolor='#1a1a1a',
        linewidth=0.3,
        label=etf,
    )
    bottom += df[etf].values

# Y축: $B 단위
def billions_formatter(x, pos):
    return f'${x:.0f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축: 월초 날짜만 라벨 표시 (주말 갭 없음)
month_ticks = []
month_labels = []
prev_month = None
for i, date in enumerate(df.index):
    if prev_month is None or date.month != prev_month:
        month_ticks.append(i)
        month_labels.append(date.strftime('%b %Y'))
        prev_month = date.month

ax.set_xticks(month_ticks)
ax.set_xticklabels(month_labels)
ax.set_xlim(-0.5, len(df) - 0.5)

# 스타일 적용
apply_style(fig, ax, 'stacked_bar')

# 폰트 크기 + 그리드
ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0, pad=20)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# =============================================================================
# 저장
# =============================================================================
output_dir = 'outputs/charts/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/btc_etf_daily_volume_stacked.png"
svg_path = f"{output_dir}/btc_etf_daily_volume_stacked.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# 통계
print(f"\nTotal period: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"Avg daily volume: ${df.sum(axis=1).mean():.2f}B")
print(f"Peak day: {df.sum(axis=1).idxmax().date()} (${df.sum(axis=1).max():.2f}B)")
print(f"IBIT avg share: {(df['IBIT'] / df.sum(axis=1)).mean()*100:.1f}%")
