"""
RWA Onchain Mcap vs DeFi Active Mcap - Area Chart
전체 RWA 발행량과 DeFi에서 실제 활용되는 규모 비교
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / '.claude/skills/design/four-pillars'))
from config import create_figure, apply_style, save_chart, SERIES_COLORS, COLORS, AXIS_CONFIG, GRID_CONFIG

# =============================================================================
# 1. 데이터 로드
# =============================================================================
base_dir = Path(__file__).resolve().parent.parent

onchain_df = pd.read_csv(base_dir / 'data/onchain_mcap.csv')
defi_df = pd.read_csv(base_dir / 'data/defi_active_mcap.csv')

# 날짜 파싱
onchain_df['Date'] = pd.to_datetime(onchain_df['Date'])
defi_df['Date'] = pd.to_datetime(defi_df['Date'])

# 카테고리 컬럼 (Timestamp, Date 제외)
category_cols_onchain = [c for c in onchain_df.columns if c not in ['Timestamp', 'Date']]
category_cols_defi = [c for c in defi_df.columns if c not in ['Timestamp', 'Date']]

# 숫자 변환 후 합계
for col in category_cols_onchain:
    onchain_df[col] = pd.to_numeric(onchain_df[col], errors='coerce').fillna(0)
for col in category_cols_defi:
    defi_df[col] = pd.to_numeric(defi_df[col], errors='coerce').fillna(0)

onchain_df['total'] = onchain_df[category_cols_onchain].sum(axis=1)
defi_df['total'] = defi_df[category_cols_defi].sum(axis=1)

# 날짜 기준 병합
merged = pd.merge(
    onchain_df[['Date', 'total']].rename(columns={'total': 'onchain_mcap'}),
    defi_df[['Date', 'total']].rename(columns={'total': 'defi_active_mcap'}),
    on='Date',
    how='inner'
)

# =============================================================================
# 2. 차트 생성
# =============================================================================
fig, ax = create_figure('area')

dates = merged['Date']
onchain = merged['onchain_mcap']
defi = merged['defi_active_mcap']

# 색상 지정
color_onchain = SERIES_COLORS[0]   # 블루
color_defi = SERIES_COLORS[3]      # 레드

# Onchain Mcap (뒤쪽, 큰 영역)
ax.fill_between(dates, onchain, alpha=0.25, color=color_onchain, linewidth=0)
ax.plot(dates, onchain, color=color_onchain, linewidth=2.0, label='Total Onchain Mcap')

# DeFi Active Mcap (앞쪽, 작은 영역)
ax.fill_between(dates, defi, alpha=0.4, color=color_defi, linewidth=0)
ax.plot(dates, defi, color=color_defi, linewidth=2.0, label='DeFi Active Mcap')

# =============================================================================
# 3. Y축 포맷팅 ($B 통일)
# =============================================================================
def format_billions(x, pos):
    return f'${x / 1e9:.0f}B'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_billions))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# Y축 0부터 시작
ax.set_ylim(bottom=0)

# =============================================================================
# 4. X축 날짜 포맷팅
# =============================================================================
import matplotlib.dates as mdates

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# X축 범위
ax.set_xlim(dates.iloc[0], dates.iloc[-1])

# =============================================================================
# 5. 스타일 적용
# =============================================================================
apply_style(fig, ax, 'area')

# X축 틱 볼드 + 회전
for label in ax.get_xticklabels():
    label.set_fontweight('bold')
    label.set_rotation(45)
    label.set_ha('right')

# Y축 틱 볼드
for label in ax.get_yticklabels():
    label.set_fontweight('bold')

# =============================================================================
# 6. 저장
# =============================================================================
output_dir = str(base_dir / 'outputs/charts/rwa')
png_path, svg_path = save_chart(fig, 'rwa_onchain_vs_defi_mcap', output_dir)
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# 최신 데이터 출력
latest = merged.iloc[-1]
print(f"\nLatest data ({latest['Date'].strftime('%Y-%m-%d')}):")
print(f"  Onchain Mcap: ${latest['onchain_mcap']/1e9:.2f}B")
print(f"  DeFi Active Mcap: ${latest['defi_active_mcap']/1e9:.2f}B")
print(f"  DeFi/Onchain ratio: {latest['defi_active_mcap']/latest['onchain_mcap']*100:.1f}%")
