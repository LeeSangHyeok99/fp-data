"""Protocol vs Holder Revenue (monthly) — 이미지 재현 (모드 B).
four-pillars 스타일: mint 바(protocol) + purple 라인(holder) + 2Q26 음영.
"""
import matplotlib
matplotlib.use('Agg')
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, apply_style, DPI, gradient_rounded_bar, endpoint_dot  # noqa: E402

setup_font()

df = pd.read_csv('outputs/data/hl_protocol_holder_revenue.csv')
months = df['month'].tolist()
protocol = df['protocol_revenue_m'].tolist()
holder = df['holder_revenue_m'].tolist()
x = list(range(len(months)))

BAR = '#a3e4cd'      # mint (protocol revenue)
LINE = '#b3a1e0'     # purple (holder revenue)
TEXT = '#d1d4dc'
SUB = '#787b86'

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# 축 범위 먼저 확정 (gradient_rounded_bar 픽셀 코너 계산에 필요)
ax.set_xlim(-0.6, len(months) - 0.4)
ax.set_ylim(0, 114)

# 2Q26 음영 (Apr, May, Jun)
q_start = months.index('Apr') - 0.5
ax.axvspan(q_start, len(months) - 0.4, color=BAR, alpha=0.07, zorder=0)
ax.text((q_start + len(months) - 0.4) / 2, 108, '2Q26', ha='center', va='center',
        fontsize=15, fontweight='bold', color=TEXT, zorder=6)

# Protocol revenue 바 (mint, 라운드 탑 + subtle 그라데이션)
width = 0.62
for xi, h in zip(x, protocol):
    gradient_rounded_bar(ax, x_center=xi, width=width, height=h, color=BAR, floor=0.82,
                         round_top=False)
    ax.text(xi, h + 2.5, f'${h:.0f}M', ha='center', va='bottom',
            fontsize=13.5, fontweight='bold', color='#ffffff', zorder=6)

# Holder revenue 라인 (purple)
ax.plot(x, holder, color=LINE, linewidth=2.6, zorder=5,
        marker='o', markersize=5.5, markerfacecolor=LINE, markeredgecolor='none')
endpoint_dot(ax, x[0], holder[0], color=LINE, size=70)
endpoint_dot(ax, x[-1], holder[-1], color=LINE, size=70)

# Y축
yt = [0, 20, 40, 60, 80, 100]
ax.set_yticks(yt)
ax.set_yticklabels([f'${v}M' for v in yt], fontsize=15, fontweight='bold', color=SUB)

# X축
ax.set_xticks(x)
ax.set_xticklabels(months, fontsize=15, fontweight='bold', color=SUB)

# 그리드 / spine
ax.grid(True, axis='y', color=SUB, alpha=0.4, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', length=6, width=1.2, color=SUB, direction='out')

fig.tight_layout()

out_dir = 'outputs/charts/hyperliquid/revenue'
png, svg = save_chart(fig, 'hl_protocol_holder_revenue', out_dir)
print('saved:', png, svg)
