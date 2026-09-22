"""
Collector Crypt Pack Tier GMV (stacked bar) - 최신화
소스: 레퍼런스 이미지 디지타이즈 (월별 티어 GMV, 26-06까지, $2500 티어 추가).
red% = $250 + $1000 + $2500 의 총 GMV 점유율 (레퍼런스 라벨 그대로).
four-pillars dark theme, 투명 배경.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI  # noqa: E402

setup_font()

df = pd.read_csv('outputs/data/cc_pack_tier_gmv_latest.csv')
df['date'] = pd.to_datetime(df['month'])

TIERS = ['p25', 'p50', 'p75', 'p80', 'p100', 'p250', 'p1000', 'p2500']
TIER_COLORS = {
    'p25': '#cfd2d6', 'p50': '#aeb2b8', 'p75': '#8b9097', 'p80': '#6b727b',
    'p100': '#2e90d9', 'p250': '#ef9343', 'p1000': '#ee6666', 'p2500': '#8b1a1a',
}

OUTPUT_DIR = 'outputs/charts/collector_crypt/gmv'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(11.5, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bottom = np.zeros(len(df))
for tier in TIERS:
    vals = df[tier].values
    ax.bar(x, vals, 0.78, bottom=bottom, color=TIER_COLORS[tier],
           edgecolor='none', zorder=3)
    bottom += vals

for xi, total, pct in zip(x, bottom, df['red_share_pct']):
    ax.text(xi, total + 2.0, f'{int(pct)}%', ha='center', va='bottom',
            fontsize=9, fontweight='bold', color='#ee6666', zorder=6)

yticks = [0, 25, 50, 75, 100]
ax.set_yticks(yticks)
ax.set_yticklabels([f'${t}M' for t in yticks], fontsize=12,
                   fontweight='bold', color=COLORS['text_secondary'])
ax.set_ylim(0, 118)

ax.set_xticks(x)
ax.set_xticklabels([d.strftime('%b %Y') for d in df['date']],
                   fontsize=10, fontweight='bold',
                   color=COLORS['text_secondary'], rotation=45, ha='right')
ax.set_xlim(-0.7, len(df) - 0.3)

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='both', length=0)

fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(f'{OUTPUT_DIR}/cc_pack_tier_gmv_latest.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True, format=fmt if fmt == 'svg' else None)
plt.close()

totals = df[TIERS].sum(axis=1)
print('Done: cc_pack_tier_gmv_latest')
print(f'  months {df.month.iloc[0]}..{df.month.iloc[-1]} | cumulative ${totals.sum():.0f}M | latest ${totals.iloc[-1]:.1f}M')
