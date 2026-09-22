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
df = pd.read_csv('outputs/data/zcash_shielded_supply.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

# M 단위
df['supply_m'] = df['shielded_supply'] / 1e6

# =============================================================================
# 브랜드 컬러 (Zcash 골드)
# =============================================================================
ZCASH_GOLD = '#F4B728'

# =============================================================================
# 차트 생성
# =============================================================================
fig, ax = create_figure('bar')

fig.patch.set_alpha(0)
ax.set_facecolor('none')

x_pos = np.arange(len(df))
bar_width = 0.78

ax.bar(
    x_pos,
    df['supply_m'].values,
    width=bar_width,
    color=ZCASH_GOLD,
    edgecolor='none',
    linewidth=0,
)

# =============================================================================
# Y축: M 단위, 0~5.2M (틱 5개 이내)
# =============================================================================
def millions_formatter(x, pos):
    if x == 0:
        return '0M'
    return f'{x:.0f}M'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions_formatter))
ax.set_ylim(0, 5.4)
ax.set_yticks([0, 1, 2, 3, 4, 5])

# =============================================================================
# X축: 약 3개월 간격으로 라벨
# =============================================================================
target_label_dates = [
    '2024-09-01', '2024-12-01',
    '2025-03-02', '2025-06-01', '2025-09-07',
    '2025-12-07', '2026-03-08',
]

date_to_idx = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(df['date'])}
month_ticks = []
month_labels = []
for d_str in target_label_dates:
    if d_str in date_to_idx:
        idx = date_to_idx[d_str]
        month_ticks.append(idx)
        month_labels.append(pd.Timestamp(d_str).strftime('%b %Y'))

ax.set_xticks(month_ticks)
ax.set_xticklabels(month_labels)
ax.set_xlim(-0.7, len(df) - 0.3)

# =============================================================================
# 스타일 적용
# =============================================================================
apply_style(fig, ax, 'bar')

ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0, pad=15, rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation_mode='anchor')

ax.grid(True, axis='y', color='#404040', alpha=0.8,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# =============================================================================
# 저장
# =============================================================================
output_dir = 'outputs/charts/zcash/supply'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/zcash_shielded_supply.png"
svg_path = f"{output_dir}/zcash_shielded_supply.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# 통계
print(f"\nPeriod: {df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}")
print(f"Weeks: {len(df)}")
print(f"Start: {df['supply_m'].iloc[0]:.2f}M ZEC")
print(f"End:   {df['supply_m'].iloc[-1]:.2f}M ZEC")
print(f"Peak:  {df['supply_m'].max():.2f}M ZEC")
print(f"Change: +{(df['supply_m'].iloc[-1] - df['supply_m'].iloc[0]):.2f}M ({((df['supply_m'].iloc[-1] / df['supply_m'].iloc[0]) - 1) * 100:.0f}%)")
