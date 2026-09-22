import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import openpyxl
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG, DPI, FIGURE_SIZES

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
wb = openpyxl.load_workbook('outputs/data/HYPE_PURR_HYPD_PRICE_CLEAN.xlsx', data_only=True)
ws = wb.active

dates = []
hype_pct = []
purr_pct = []
hypd_pct = []

for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=7, max_col=10, values_only=True):
    if row[0] is not None:
        dates.append(row[0])
        hype_pct.append(row[1] if row[1] is not None else 0)
        purr_pct.append(row[2] if row[2] is not None else 0)
        hypd_pct.append(row[3] if row[3] is not None else 0)

df = pd.DataFrame({
    'date': dates,
    'HYPE': hype_pct,
    'PURR': purr_pct,
    'HYPD': hypd_pct,
})
df['date'] = pd.to_datetime(df['date'])

# =============================================================================
# 브랜드 컬러
# =============================================================================
BRAND_COLORS = {
    'HYPE': '#1a7ab5',   # 틸 블루
    'PURR': '#e88c2a',   # 오렌지
    'HYPD': '#2d7d3f',   # 다크 그린
}

# =============================================================================
# 차트 생성 (Four Pillars 다크 테마)
# =============================================================================
fig, ax = create_figure('multi-line')

# 투명 배경
fig.patch.set_alpha(0)
ax.set_facecolor('none')

for token in ['HYPE', 'PURR', 'HYPD']:
    ax.plot(
        df['date'],
        df[token],
        color=BRAND_COLORS[token],
        linewidth=2.5,
        label=token,
    )

# Y축: 퍼센트 포맷
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축: 시작일 + 월초 틱
import datetime
start_date = df['date'].iloc[0]
month_starts = pd.date_range(start='2026-01-01', end=df['date'].iloc[-1], freq='MS')
tick_dates = [start_date] + list(month_starts)
ax.set_xticks(tick_dates)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(start_date, df['date'].iloc[-1])

# 0% 기준선
ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=0.8, alpha=0.6)

# 스타일 적용
apply_style(fig, ax, 'multi-line')


# 폰트 크기 키우기
ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0)

# Y축 그리드 강화 (다크 배경에서 잘 보이도록)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.grid(True, axis='x', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# Y축 하단과 X축 라벨 간격 확보
ax.set_ylim(-0.50, 0.40)
ax.tick_params(axis='x', pad=20)

# =============================================================================
# 저장 (다크 배경 포함)
# =============================================================================
output_dir = 'outputs/charts/hyperliquid'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/hype_purr_hypd_price_performance.png"
svg_path = f"{output_dir}/hype_purr_hypd_price_performance.svg"

fig.savefig(
    png_path,
    dpi=DPI,
    facecolor='none',
    edgecolor='none',
    bbox_inches='tight',
)
fig.savefig(
    svg_path,
    format='svg',
    facecolor='none',
    edgecolor='none',
    bbox_inches='tight',
)

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
