import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import COLORS, GRID_CONFIG, save_chart, setup_font

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('sources/figure11_monad_top10_tvl.csv')

SECTOR_COLORS = {
    'Lending': '#836EF9',            # Monad Purple
    'Yield': '#85E6FF',              # 스카이 시안
    'RWA': '#DDD7FE',                # 라이트 라벤더
    'DEX': '#B9E3F9',                # 페일 블루
    'Capital Allocator': '#0E091C',  # 딥 다크 네이비
}

setup_font()

# =============================================================================
# Chart: horizontal bar, rank 1 on top, sector color coding
# =============================================================================
fig, ax = plt.subplots(figsize=(15.0, 6.4), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = range(len(df))
colors = [SECTOR_COLORS[s] for s in df['sector']]
ax.barh(y, df['tvl_usd_m'], color=colors, height=0.62, zorder=3)
ax.invert_yaxis()  # rank 1 위로

# 프로토콜 이름 (좌측)
ax.set_yticks(list(y))
ax.set_yticklabels(df['protocol'])
ax.tick_params(axis='y', labelsize=20, pad=12, length=0,
               colors=COLORS['text'])

# 값 라벨 (바 우측 끝)
for i, v in enumerate(df['tvl_usd_m']):
    ax.annotate(f'${v:.1f}M', xy=(v + 2, i), va='center', ha='left',
                fontsize=18, fontweight='bold',
                color=COLORS['text_secondary'])

# X축 틱 + 세로 그리드
ax.set_xticks([0, 50, 100])
ax.set_xticklabels(['$0M', '$50M', '$100M'])
ax.set_xlim(0, 155)
ax.tick_params(axis='x', labelsize=18, pad=10, length=0,
               colors=COLORS['text_secondary'])
ax.grid(
    True,
    axis='x',
    color=GRID_CONFIG['color'],
    alpha=GRID_CONFIG['alpha'],
    linestyle=GRID_CONFIG['linestyle'],
    linewidth=GRID_CONFIG['linewidth'],
)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
png, svg = save_chart(fig, 'monad_top10_protocols_tvl',
                      'outputs/charts/monad/tvl')
plt.close(fig)
print(png)
