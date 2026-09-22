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
# Chart: smooth crossover with glow
# =============================================================================
fig, ax = create_figure('multi-line')

xnum = mdates.date2num(df['date'])
xs, kuru_s = pchip_smooth(xnum, df['kuru_share_pct'].values)
_, uni_s = pchip_smooth(xnum, df['uniswap_share_pct'].values)

# 라인 아래 글로우 (라인 근처에 집중)
for i in range(30):
    frac = i / 30
    ax.fill_between(xs, kuru_s * frac, kuru_s * (frac + 1 / 30),
                    color=COLOR_KURU, alpha=0.16 * frac**2.5,
                    linewidth=0, zorder=2)
    ax.fill_between(xs, uni_s * frac, uni_s * (frac + 1 / 30),
                    color=COLOR_UNISWAP, alpha=0.10 * frac**2.5,
                    linewidth=0, zorder=1)

ax.plot(xs, uni_s, color=COLOR_UNISWAP, linewidth=3.2, zorder=4,
        solid_capstyle='round')
ax.plot(xs, kuru_s, color=COLOR_KURU, linewidth=3.8, zorder=5,
        solid_capstyle='round')

# 월별 데이터 포인트 도트
ax.scatter(xnum, df['kuru_share_pct'], s=42, color=COLOR_KURU,
           zorder=6, edgecolors='#141414', linewidths=1.5)
ax.scatter(xnum, df['uniswap_share_pct'], s=42, color=COLOR_UNISWAP,
           zorder=6, edgecolors='#141414', linewidths=1.5)

# 크로스오버 포인트 하이라이트 (스무딩 곡선 교차점)
ci = np.argwhere(np.diff(np.sign(kuru_s - uni_s))).flatten()
if len(ci):
    cx, cy = xs[ci[-1]], kuru_s[ci[-1]]
    ax.scatter([cx], [cy], s=340, facecolors='none',
               edgecolors=COLOR_LABEL, linewidths=1.6, zorder=7)
    ax.axvline(cx, color=COLOR_LABEL, linewidth=1.0, linestyle=(0, (4, 4)),
               alpha=0.35, zorder=1)

# 끝점 강조 + 인라인 라벨
ax.scatter([xnum[-1]], [df['kuru_share_pct'].iloc[-1]], s=120,
           color=COLOR_KURU, zorder=7, edgecolors='#141414', linewidths=1.5)
ax.scatter([xnum[-1]], [df['uniswap_share_pct'].iloc[-1]], s=120,
           color=COLOR_UNISWAP, zorder=7, edgecolors='#141414', linewidths=1.5)
ax.annotate(f"Kuru {df['kuru_share_pct'].iloc[-1]:.1f}%",
            xy=(xnum[-1], df['kuru_share_pct'].iloc[-1]),
            xytext=(6, 18), textcoords='offset points',
            ha='right', va='bottom',
            fontsize=23, fontweight='bold', color=COLOR_LABEL, zorder=8)
ax.annotate(f"Uniswap {df['uniswap_share_pct'].iloc[-1]:.1f}%",
            xy=(xnum[-1], df['uniswap_share_pct'].iloc[-1]),
            xytext=(6, -20), textcoords='offset points',
            ha='right', va='top',
            fontsize=23, fontweight='bold', color=COLOR_UNISWAP, zorder=8)

# 시작점 라벨 (1.2% / 69.1%)
ax.annotate('1.2%', xy=(xnum[0], df['kuru_share_pct'].iloc[0]),
            xytext=(0, 14), textcoords='offset points',
            ha='left', va='bottom',
            fontsize=19, fontweight='bold', color=COLOR_KURU, zorder=8)
ax.annotate('69.1%', xy=(xnum[0], df['uniswap_share_pct'].iloc[0]),
            xytext=(0, 14), textcoords='offset points',
            ha='left', va='bottom',
            fontsize=19, fontweight='bold', color=COLOR_UNISWAP, zorder=8)

# Y axis: 0~80%, 20%p 간격 (5 ticks)
y_ticks = [0, 20, 40, 60, 80]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks])
ax.set_ylim(0, 80)

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.margins(x=0.02)

apply_style(fig, ax, 'multi-line')

png, svg = save_chart(fig, 'monad_kuru_flip_glow', 'outputs/charts/monad/dex')
plt.close(fig)
print(png)
