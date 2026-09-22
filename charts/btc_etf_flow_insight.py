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
from config import create_figure, apply_style, setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/btc_etf_daily_flow.csv', parse_dates=['Date'])
df = df.set_index('Date')

# 숫자 변환
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# =============================================================================
# 차트 1: IBIT vs GBTC 누적 Flow (대이동 스토리)
# =============================================================================
setup_font()
fig, ax = create_figure('line')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ibit_cum = df['IBIT'].fillna(0).cumsum()
gbtc_cum = df['GBTC'].fillna(0).cumsum()

x_pos = np.arange(len(df))

# IBIT (BlackRock 다크 네이비 → 여기선 가시성 위해 밝은 블루)
ax.plot(x_pos, ibit_cum.values / 1000, color='#4A90D9', linewidth=2.0)
ax.fill_between(x_pos, ibit_cum.values / 1000, 0, alpha=0.12, color='#4A90D9')

# GBTC (Grayscale 그레이)
ax.plot(x_pos, gbtc_cum.values / 1000, color='#8B8B8B', linewidth=2.0)
ax.fill_between(x_pos, gbtc_cum.values / 1000, 0, alpha=0.12, color='#ef5350')

# Y축: $B
def billions_fmt(x, pos):
    return f'${x:+.0f}B' if x != 0 else '$0B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축
month_ticks = []
month_labels = []
prev = None
for i, date in enumerate(df.index):
    if prev is None or (date.year, date.month) != prev:
        if date.month in [1, 4, 7, 10]:
            month_ticks.append(i)
            month_labels.append(date.strftime('%b %Y'))
        prev = (date.year, date.month)
ax.set_xticks(month_ticks)
ax.set_xticklabels(month_labels)
ax.set_xlim(-0.5, len(df) - 0.5)

# 0선
ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=0.5, alpha=0.5)

# 스타일
apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=0, pad=15)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

output_dir = 'outputs/charts/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/btc_etf_ibit_vs_gbtc.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_ibit_vs_gbtc.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Chart 1: {output_dir}/btc_etf_ibit_vs_gbtc.png")

# =============================================================================
# 차트 2: Monthly Net Flow (Glassnode 데이터 사용)
# =============================================================================
gn = pd.read_csv('outputs/data/btc_etf_monthly_flow_glassnode.csv')
gn['Date'] = pd.to_datetime(gn['Date'])
gn = gn.set_index('Date')
monthly = gn['NetFlow_B']

fig, ax = create_figure('stacked_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

colors = ['#26a69a' if v >= 0 else '#ef5350' for v in monthly.values]
x_pos_m = np.arange(len(monthly))

ax.bar(x_pos_m, monthly.values, width=0.7, color=colors, edgecolor='none')

# Y축
def billions_fmt2(x, pos):
    return f'${x:.1f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt2))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축
tick_idx = [i for i, d in enumerate(monthly.index) if d.month % 2 == 1]
ax.set_xticks([x_pos_m[i] for i in tick_idx])
ax.set_xticklabels([monthly.index[i].strftime('%b %Y') for i in tick_idx], fontsize=11, rotation=0, ha='center')
ax.set_xlim(-0.5, len(monthly) - 0.5)

ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=0.5, alpha=0.5)

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=12, length=0, pad=10)
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.savefig(f'{output_dir}/btc_etf_monthly_flow.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_monthly_flow.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Chart 2: {output_dir}/btc_etf_monthly_flow.png")

# =============================================================================
# 통계
# =============================================================================
print(f"\n--- IBIT vs GBTC ---")
print(f"IBIT cumulative: +${ibit_cum.iloc[-1]/1000:.1f}B")
print(f"GBTC cumulative: ${gbtc_cum.iloc[-1]/1000:.1f}B")
print(f"Gap: ${(ibit_cum.iloc[-1] - abs(gbtc_cum.iloc[-1]))/1000:.1f}B")

print(f"\n--- Monthly Flow ---")
for date, val in monthly.items():
    print(f"  {date.strftime('%Y-%m')}: ${val:+.2f}B")

print(f"\nBest month: {monthly.idxmax().strftime('%Y-%m')} (${monthly.max():+.2f}B)")
print(f"Worst month: {monthly.idxmin().strftime('%Y-%m')} (${monthly.min():+.2f}B)")
print(f"Positive months: {(monthly > 0).sum()}, Negative months: {(monthly < 0).sum()}")
