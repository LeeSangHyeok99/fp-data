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

# Bars = monthly KRW volume (trillions, left); line = new listings (right).
# Aug is partial (through Aug 19) -> muted bar.
df = pd.read_csv('sources/chart-1-data.csv')
df['label'] = pd.to_datetime(df['month']).dt.strftime('%b %Y')
df.loc[df['is_partial'] == True, 'label'] += '*'

BAR_COLOR = '#5470c6'
BAR_PARTIAL = '#8fa3e0'
LINE_COLOR = '#ee6666'

OUTPUT_DIR = 'outputs/charts/upbit/listings'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2 = ax.twinx()
ax2.set_facecolor('none')

x = np.arange(len(df))

# 좌/우 축 틱 5개, 80T <-> 16 listings 가 같은 그리드에 오도록 ylim 비율을 맞춘다
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_yticklabels([f'₩{t}T' for t in [0, 20, 40, 60, 80]],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.set_ylim(0, 95)
ax2.set_yticks([0, 4, 8, 12, 16])
ax2.set_yticklabels([str(t) for t in [0, 4, 8, 12, 16]],
                    fontsize=19, fontweight='bold', color=LINE_COLOR)
ax2.set_ylim(0, 19)
ax.set_xlim(-0.6, len(df) - 0.4)

for xi, v, partial in zip(x, df['monthly_volume_krw_trillions'], df['is_partial']):
    gradient_rounded_bar(ax, xi, 0.50, v,
                         BAR_PARTIAL if partial else BAR_COLOR, floor=0.52,
                         round_top=False)
    # 라벨이 그리드선(20T 간격)에 걸리면 선 위로 올린다
    top = v + 2.2
    g = 20 * np.ceil(top / 20)
    if g < top + 4.6:
        top = g + 0.8
    ax.text(xi, top, f'₩{v:.0f}T', ha='center', va='bottom',
            fontsize=17, fontweight='bold', color=COLORS['text'], zorder=6)

ax2.plot(x, df['new_listings'], color=LINE_COLOR, linewidth=3.4,
         marker='o', markersize=9, zorder=5)

# 라인 라벨은 피크와 마지막 달만. 나머지는 바 라벨과 겹쳐 읽기 나빠진다.
for xi in (df['new_listings'].idxmax(), len(df) - 1):
    v = df['new_listings'].iloc[xi]
    ax2.text(xi, v + 0.6, str(v), ha='center', va='bottom',
             fontsize=14, fontweight='bold', color=LINE_COLOR, zorder=6)

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
    fig.savefig(f'{OUTPUT_DIR}/upbit_listings_vs_volume.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close()

print('Done: upbit_listings_vs_volume')
print(f"  Volume ₩{df['monthly_volume_krw_trillions'].iloc[0]:.0f}T -> "
      f"₩{df['monthly_volume_krw_trillions'].iloc[-1]:.0f}T "
      f"({df['monthly_volume_krw_trillions'].iloc[-1] / df['monthly_volume_krw_trillions'].iloc[0] - 1:+.0%})")
print(f"  Listings {df['new_listings'].iloc[0]} -> {df['new_listings'].iloc[-1]} "
      f"| peak {df['new_listings'].max()} ({df['label'].iloc[df['new_listings'].idxmax()]})")
