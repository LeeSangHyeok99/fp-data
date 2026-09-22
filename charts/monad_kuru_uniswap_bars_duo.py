import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, gradient_rounded_bar, save_chart

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/monad_kuru_uniswap_share.csv')
df['date'] = pd.to_datetime(df['month'] + '-01')

COLOR_KURU = '#836EF9'     # Monad Purple
COLOR_UNISWAP = '#A0055D'  # Monad Berry
COLOR_LABEL = '#E9CFFC'    # Monad Lavender

# =============================================================================
# Chart: paired gradient rounded bars (Uniswap vs Kuru)
# =============================================================================
fig, ax = create_figure('bar')

off = 0.21
for i, row in df.iterrows():
    gradient_rounded_bar(ax, x_center=i - off, width=0.36,
                         height=row['uniswap_share_pct'], color=COLOR_UNISWAP)
    gradient_rounded_bar(ax, x_center=i + off, width=0.36,
                         height=row['kuru_share_pct'], color=COLOR_KURU)

# 첫 달 / 마지막 달 수치 라벨로 반전 강조
ax.annotate('69.1%', xy=(0 - off, df['uniswap_share_pct'].iloc[0] + 1.5),
            ha='center', va='bottom', fontsize=19, fontweight='bold',
            color=COLOR_UNISWAP, zorder=6)
ax.annotate('1.2%', xy=(0 + off, df['kuru_share_pct'].iloc[0] + 1.5),
            ha='center', va='bottom', fontsize=19, fontweight='bold',
            color=COLOR_KURU, zorder=6)
n = len(df) - 1
ax.annotate('32.0%', xy=(n - off, df['uniswap_share_pct'].iloc[-1] + 1.2),
            ha='center', va='bottom', fontsize=16, fontweight='bold',
            color=COLOR_UNISWAP, zorder=6)
ax.annotate('36.4%', xy=(n + off, df['kuru_share_pct'].iloc[-1] + 1.2),
            ha='center', va='bottom', fontsize=16, fontweight='bold',
            color=COLOR_LABEL, zorder=6)

# 시리즈 이름 인라인 라벨 (범례 대체, 첫 바 오른쪽 여백)
ax.annotate('Uniswap', xy=(0 + off + 0.28, 66),
            ha='left', va='bottom', fontsize=22, fontweight='bold',
            color=COLOR_UNISWAP, zorder=6)
ax.annotate('Kuru', xy=(n + off, df['kuru_share_pct'].iloc[-1] + 10),
            ha='center', va='bottom', fontsize=22, fontweight='bold',
            color=COLOR_KURU, zorder=6)

# Y axis: 0~80%, 20%p 간격 (5 ticks)
y_ticks = [0, 20, 40, 60, 80]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks])
ax.set_ylim(0, 80)

# X axis
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df['date'].dt.strftime('%b %Y'))
ax.set_xlim(-0.7, len(df) - 0.3)

apply_style(fig, ax, 'bar')

png, svg = save_chart(fig, 'monad_kuru_uniswap_bars_duo',
                      'outputs/charts/monad/dex')
plt.close(fig)
print(png)
