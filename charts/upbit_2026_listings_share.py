import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, gradient_rounded_bar

setup_font()

# Bars = volume from coins listed in 2026 (KRW trillions, left);
# line = that volume's share of total KRW-market volume (right).
# Aug is partial (through Aug 19) -> muted bar, dashed last line segment.
df = pd.read_csv('sources/chart-2-data.csv')
df['label'] = pd.to_datetime(df['month']).dt.strftime('%b %Y')
df.loc[df['is_partial'] == True, 'label'] += '*'

BAR_COLOR = '#5470c6'
BAR_PARTIAL = '#8fa3e0'
LINE_COLOR = '#ee6666'
GRID_STEP = 5.0

OUTPUT_DIR = 'outputs/charts/upbit/listings'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2 = ax.twinx()
ax2.set_facecolor('none')

x = np.arange(len(df))

# 좌/우 축 틱 개수를 맞춰 그리드가 정확히 대응되게 한다 (₩10T <-> 30%)
ax.set_yticks([0, 5, 10])
ax.set_yticklabels([f'₩{t}T' for t in [0, 5, 10]],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.set_ylim(0, 11.9)
ax2.set_yticks([0, 15, 30])
ax2.set_yticklabels([f'{t}%' for t in [0, 15, 30]],
                    fontsize=19, fontweight='bold', color=LINE_COLOR)
ax2.set_ylim(0, 35.7)
ax.set_xlim(-0.6, len(df) - 0.4)

for xi, v, partial in zip(x, df['volume_from_2026_listings_krw_trillions'],
                          df['is_partial']):
    gradient_rounded_bar(ax, xi, 0.50, v,
                         BAR_PARTIAL if partial else BAR_COLOR, floor=0.52,
                         round_top=False)
    # 라벨이 그리드선에 걸리면 선 위로 올린다
    top = v + 0.28
    g = GRID_STEP * np.ceil(top / GRID_STEP)
    if g < top + 0.58:
        top = g + 0.1
    ax.text(xi, top, f'₩{v:.1f}T', ha='center', va='bottom',
            fontsize=17, fontweight='bold', color=COLORS['text'], zorder=6)

# 마지막 구간(부분 집계 8월)만 점선
s = df['share_of_total_pct']
ax2.plot(x[:-1], s[:-1], color=LINE_COLOR, linewidth=3.4, marker='o',
         markersize=9, zorder=5)
ax2.plot(x[-2:], s[-2:], color=LINE_COLOR, linewidth=3.4, linestyle=(0, (2, 1.4)),
         marker='o', markersize=9, zorder=5)

# 라인 라벨은 점 위. 마지막 점은 오른쪽 끝이라 안쪽으로 살짝 당긴다.
for xi in x[:-1]:
    ax2.text(xi, s.iloc[xi] + 1.2, f'{s.iloc[xi]:.1f}%', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color=LINE_COLOR, zorder=6)
ax2.text(len(df) - 1.08, s.iloc[-1] + 1.2, f'{s.iloc[-1]:.1f}%', ha='right',
         va='bottom', fontsize=14, fontweight='bold', color=LINE_COLOR, zorder=6)

ax.set_xticks(x)
ax.set_xticklabels(df['label'], fontsize=13, fontweight='bold',
                   color=COLORS['text'], rotation=45, ha='right')

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in list(ax.spines.values()) + list(ax2.spines.values()):
    spine.set_visible(False)
ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', length=6, width=1, color=COLORS['text_secondary'], pad=6)
ax2.tick_params(axis='both', length=0)

fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(f'{OUTPUT_DIR}/upbit_2026_listings_share.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close()

print('Done: upbit_2026_listings_share')
print(f"  Share {s.iloc[0]:.1f}% -> {s.iloc[-1]:.1f}% | peak volume "
      f"₩{df['volume_from_2026_listings_krw_trillions'].max():.1f}T "
      f"({df['label'].iloc[df['volume_from_2026_listings_krw_trillions'].idxmax()]})")
