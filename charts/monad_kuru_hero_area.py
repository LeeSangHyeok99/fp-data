import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, save_chart

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/monad_kuru_uniswap_share.csv')
df['date'] = pd.to_datetime(df['month'] + '-01')

COLOR_KURU = '#836EF9'     # Monad Purple
COLOR_UNISWAP = '#A0055D'  # Monad Berry
COLOR_LABEL = '#E9CFFC'    # Monad Lavender


def pchip_smooth(x, y, n=400):
    """Fritsch-Carlson monotone cubic 보간 (오버슈트 없는 부드러운 곡선)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    h = np.diff(x)
    m = np.diff(y) / h
    d = np.zeros_like(y)
    for k in range(1, len(y) - 1):
        if m[k - 1] * m[k] > 0:
            w1 = 2 * h[k] + h[k - 1]
            w2 = h[k] + 2 * h[k - 1]
            d[k] = (w1 + w2) / (w1 / m[k - 1] + w2 / m[k])
    d[0] = ((2 * h[0] + h[1]) * m[0] - h[0] * m[1]) / (h[0] + h[1])
    if np.sign(d[0]) != np.sign(m[0]):
        d[0] = 0
    elif np.sign(m[0]) != np.sign(m[1]) and abs(d[0]) > abs(3 * m[0]):
        d[0] = 3 * m[0]
    d[-1] = ((2 * h[-1] + h[-2]) * m[-1] - h[-1] * m[-2]) / (h[-1] + h[-2])
    if np.sign(d[-1]) != np.sign(m[-1]):
        d[-1] = 0
    elif np.sign(m[-1]) != np.sign(m[-2]) and abs(d[-1]) > abs(3 * m[-1]):
        d[-1] = 3 * m[-1]

    xs = np.linspace(x[0], x[-1], n)
    ys = np.empty_like(xs)
    idx = np.clip(np.searchsorted(x, xs) - 1, 0, len(x) - 2)
    for i, (xi, k) in enumerate(zip(xs, idx)):
        t = (xi - x[k]) / h[k]
        h00 = 2 * t**3 - 3 * t**2 + 1
        h10 = t**3 - 2 * t**2 + t
        h01 = -2 * t**3 + 3 * t**2
        h11 = t**3 - t**2
        ys[i] = (h00 * y[k] + h10 * h[k] * d[k]
                 + h01 * y[k + 1] + h11 * h[k] * d[k + 1])
    return xs, ys


# =============================================================================
# Chart: Kuru hero area (vertical gradient fill) + dim Uniswap reference
# =============================================================================
fig, ax = create_figure('area')

xnum = mdates.date2num(df['date'])
xs, kuru_s = pchip_smooth(xnum, df['kuru_share_pct'].values)
_, uni_s = pchip_smooth(xnum, df['uniswap_share_pct'].values)

# Uniswap: 은은한 레퍼런스 라인
ax.plot(xs, uni_s, color=COLOR_UNISWAP, linewidth=2.4, alpha=0.85,
        zorder=3, solid_capstyle='round')

# Kuru: 히어로 라인 (글로우 레이어 + 본선)
for lw, a in [(11, 0.08), (7, 0.14), (4.6, 0.22)]:
    ax.plot(xs, kuru_s, color=COLOR_KURU, linewidth=lw, alpha=a,
            zorder=4, solid_capstyle='round')
ax.plot(xs, kuru_s, color='#A493FB', linewidth=3.4, zorder=5,
        solid_capstyle='round')

# 끝점 도트는 9월(최신), 값 라벨은 제목 기준 8월
i_aug = df.index[df['month'] == '2026-08'][0]
ax.scatter([xnum[-1]], [df['kuru_share_pct'].iloc[-1]], s=70,
           color=COLOR_LABEL, zorder=7, edgecolors=COLOR_KURU,
           linewidths=1.8, clip_on=False)
ax.scatter([xnum[-1]], [df['uniswap_share_pct'].iloc[-1]], s=70,
           color='#F2D5E6', zorder=7, edgecolors=COLOR_UNISWAP,
           linewidths=1.8, clip_on=False)
ax.annotate(f"Aug\nKuru {df['kuru_share_pct'].iloc[i_aug]:.1f}%",
            xy=(xnum[i_aug], df['kuru_share_pct'].iloc[i_aug]),
            xytext=(0, 12), textcoords='offset points',
            ha='center', va='bottom',
            fontsize=16, fontweight='bold', color=COLOR_KURU, zorder=8)
# Uniswap 라벨은 라인 시작부 위 (끝부분은 Kuru와 겹침)
ax.annotate(f"Uniswap {df['uniswap_share_pct'].iloc[0]:.1f}%",
            xy=(xnum[0], df['uniswap_share_pct'].iloc[0]),
            xytext=(4, 14), textcoords='offset points',
            ha='left', va='bottom',
            fontsize=15, fontweight='bold', color=COLOR_UNISWAP, zorder=8)
ax.annotate(f"Aug\nUniswap {df['uniswap_share_pct'].iloc[i_aug]:.1f}%",
            xy=(xnum[i_aug], df['uniswap_share_pct'].iloc[i_aug]),
            xytext=(0, -12), textcoords='offset points',
            ha='center', va='top',
            fontsize=15, fontweight='bold', color=COLOR_UNISWAP, zorder=8)
ax.annotate(f"Kuru {df['kuru_share_pct'].iloc[0]:.1f}%", xy=(xnum[0], df['kuru_share_pct'].iloc[0]),
            xytext=(4, 14), textcoords='offset points',
            ha='left', va='bottom',
            fontsize=16, fontweight='bold', color=COLOR_KURU, zorder=8)

# Y axis: 0~80%, 20%p 간격 (5 ticks)
y_ticks = [0, 20, 40, 60, 80]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks])
ax.set_ylim(0, 80)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.margins(x=0.02)

apply_style(fig, ax, 'area')

# 축 틱 폰트 축소 (기본 y 24 / x 22), 각 축 내 크기 통일
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'monad_kuru_hero_area', 'outputs/charts/monad/dex')
plt.close(fig)
print(png)
