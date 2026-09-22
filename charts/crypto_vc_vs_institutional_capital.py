"""
Crypto-native VC vs Institutional Capital Inflows (연도별 스택 바) - four-pillars 내재화
데이터: 사용자 제공 (DefiLlama raises 기반 투자자 타입 분류, 2026은 YTD).
투자자 타입별 attributed capital. 라운드 금액을 공개 투자자 수로 균등 배분한 값.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI  # noqa: E402

BAR_W = 0.62


def grad_segment(ax, xc, y0, h, color):
    """스택 세그먼트를 세로 그라데이션(아래 어둡게 → 위 밝게)으로 채운다."""
    if h <= 0:
        return
    x_left, x_right = xc - BAR_W / 2, xc + BAR_W / 2
    r, g, b = mcolors.to_rgb(color)
    f = 0.72 + 0.40 * np.linspace(0, 1, 256)
    grad = np.stack([np.clip(r * f, 0, 1), np.clip(g * f, 0, 1),
                     np.clip(b * f, 0, 1), np.ones(256)], axis=-1)[:, None, :]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, y0, y0 + h], zorder=3,
                   interpolation='bilinear')
    clip = Rectangle((x_left, y0), BAR_W, h, transform=ax.transData,
                     facecolor='none', edgecolor='none')
    ax.add_patch(clip)
    im.set_clip_path(clip)


df = pd.read_csv('outputs/data/crypto_vc_vs_institutional_capital.csv')

# 스택 순서(아래 → 위). 크립토 네이티브는 민트, 기관은 블루→핑크 램프로
# 하나의 블록처럼 읽히게 한다.
SERIES = [
    ('crypto_native_vc',      '#50e3c2'),  # Crypto-native VC
    ('inst_generalist_vc',    '#4a7fd4'),  # Generalist VC / Growth / PE
    ('inst_tradfi_am_mi',     '#6d6ce0'),  # TradFi / Asset Manager / Market Infra
    ('inst_corporate_cvc',    '#9a72d8'),  # Corporate / CVC
    ('inst_sovereign',        '#c47ec8'),  # Sovereign / Government-backed
    ('inst_tradfi_crypto_arm','#e08fa8'),  # TradFi Crypto Arm
]

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bottom = np.zeros(len(df))
for col, color in SERIES:
    vals = df[col].values / 1e9  # USD -> $B
    for xi, b, v in zip(x, bottom, vals):
        grad_segment(ax, xi, b, v, color)
    bottom += vals

yticks = [0, 5, 10, 15, 20]
ax.set_yticks(yticks)
ax.set_yticklabels([f'${t}B' for t in yticks])
ax.set_ylim(0, 22)

ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str))
ax.set_xlim(-0.7, len(df) - 0.3)

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
name = 'crypto_vc_vs_institutional_capital'
fig.savefig(f'{OUTPUT_DIR}/{name}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{OUTPUT_DIR}/{name}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

# 스택 합이 입력 데이터 총합과 일치하는지 확인
expected = df[[c for c, _ in SERIES]].sum(axis=1).values / 1e9
assert np.allclose(bottom, expected), 'stack total mismatch'
assert bottom.max() <= 22, f'ylim too low: max {bottom.max():.2f}B'
print(f'PNG: {OUTPUT_DIR}/{name}.png')
print('yearly totals ($B):',
      ', '.join(f'{y}={v:.2f}' for y, v in zip(df['year'], bottom)))
