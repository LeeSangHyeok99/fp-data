import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/btc_etf_daily_flow.csv', parse_dates=['Date'])
df = df.set_index('Date')

# Total 컬럼 사용 (US$m 단위)
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df = df.dropna(subset=['Total'])
df = df[df['Total'] != 0]

# =============================================================================
# 차트 1: Net Flow (바 차트)
# =============================================================================
fig, ax = create_figure('stacked_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x_pos = np.arange(len(df))
colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df['Total']]

ax.bar(x_pos, df['Total'], width=0.8, color=colors, edgecolor='none', linewidth=0)

# Y축: $M 단위
def millions_formatter(x, pos):
    if abs(x) >= 1000:
        return f'${x/1000:.1f}B'
    return f'${x:.0f}M'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions_formatter))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축: 월초 라벨
month_ticks = []
month_labels = []
prev_month = None
for i, date in enumerate(df.index):
    if prev_month is None or (date.year, date.month) != prev_month:
        # 분기 시작월만 표시 (너무 많으면 가독성 저하)
        if date.month in [1, 4, 7, 10]:
            month_ticks.append(i)
            month_labels.append(date.strftime('%b %Y'))
        prev_month = (date.year, date.month)

ax.set_xticks(month_ticks)
ax.set_xticklabels(month_labels)
ax.set_xlim(-0.5, len(df) - 0.5)

# 0선
ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=0.5, alpha=0.5)

# 스타일
apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=0, pad=15)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# 저장
output_dir = 'outputs/charts/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/btc_etf_net_flow.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_net_flow.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Flow chart saved: {output_dir}/btc_etf_net_flow.png")

# =============================================================================
# 차트 2: Cumulative Net Flow (AUM proxy - 누적 유입액)
# =============================================================================
df['Cumulative'] = df['Total'].cumsum()

fig, ax = create_figure('line')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 라인
ax.plot(x_pos, df['Cumulative'].values, color='#00A3FF', linewidth=1.8)
ax.fill_between(x_pos, df['Cumulative'].values, 0, alpha=0.15, color='#00A3FF')

# Y축: $B 단위
def billions_formatter(x, pos):
    return f'${x/1000:.1f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축: 같은 방식
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_labels)
ax.set_xlim(-0.5, len(df) - 0.5)

# 스타일
apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=0, pad=15)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.savefig(f'{output_dir}/btc_etf_cumulative_flow.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_cumulative_flow.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Cumulative flow chart saved: {output_dir}/btc_etf_cumulative_flow.png")

# =============================================================================
# 통계
# =============================================================================
print(f"\n--- BTC ETF Flow Stats ---")
print(f"Period: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"Total net inflow: ${df['Total'].sum():,.0f}M (${df['Total'].sum()/1000:.1f}B)")
print(f"Avg daily flow: ${df['Total'].mean():,.1f}M")
print(f"Max inflow day: {df['Total'].idxmax().date()} (${df['Total'].max():,.1f}M)")
print(f"Max outflow day: {df['Total'].idxmin().date()} (${df['Total'].min():,.1f}M)")
print(f"Inflow days: {(df['Total'] > 0).sum()}, Outflow days: {(df['Total'] < 0).sum()}")
print(f"Cumulative (latest): ${df['Cumulative'].iloc[-1]:,.0f}M (${df['Cumulative'].iloc[-1]/1000:.1f}B)")
