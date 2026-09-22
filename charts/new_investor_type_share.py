"""
Share of New Crypto-native VC vs New Institutional Investors (연도별 라인) - four-pillars 내재화
데이터: 사용자 제공. New = 해당 연도에 처음 등장한 투자자. 2026은 YTD.
색상은 crypto_vc_vs_institutional_capital 차트와 맞춤 (크립토 네이티브=민트).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI  # noqa: E402

MINT = '#50e3c2'    # New Crypto-native VC
PURPLE = '#b9a7e8'  # New Institutional

df = pd.read_csv('outputs/data/new_investor_type_share.csv')
x = np.arange(len(df))

setup_font()
fig, ax = plt.subplots(figsize=(13.33, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

for col, color in [('crypto_native_vc_share', MINT),
                   ('institutional_share', PURPLE)]:
    ax.plot(x, df[col], color=color, linewidth=2.6, marker='o',
            markersize=7, markeredgecolor='none', zorder=5)

# 50% 기준선 (두 시리즈가 교차하는 지점)
ax.axhline(50, color=COLORS['text_secondary'], alpha=0.35,
           linewidth=1.0, linestyle=(0, (2, 3)), zorder=1)

yticks = [0, 25, 50, 75, 100]
ax.set_yticks(yticks)
ax.set_yticklabels([f'{t}%' for t in yticks])
ax.set_ylim(-4, 104)

labels = [f'{y}\nYTD' if y == 2026 else str(y) for y in df['year']]
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlim(-0.5, len(df) - 0.5)

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=18, length=0, pad=12,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=15, length=6, width=1, pad=8,
               colors=COLORS['text_secondary'])
for lb in ax.get_xticklabels() + ax.get_yticklabels():
    lb.set_fontweight('bold')

fig.tight_layout()

OUTPUT_DIR = 'outputs/charts/crypto_funding/vc'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
name = 'new_investor_type_share'
fig.savefig(f'{OUTPUT_DIR}/{name}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{OUTPUT_DIR}/{name}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

# 두 시리즈 합이 100%인지, 카운트 비율과 일치하는지 확인
total = df['crypto_native_vc_share'] + df['institutional_share']
assert np.allclose(total, 100, atol=0.02), f'share sum != 100: {total.tolist()}'
calc = df['crypto_native_vc_count'] / (
    df['crypto_native_vc_count'] + df['institutional_count']) * 100
assert np.allclose(calc, df['crypto_native_vc_share'], atol=0.02), 'share/count mismatch'
print(f'PNG: {OUTPUT_DIR}/{name}.png')
