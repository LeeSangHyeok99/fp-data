"""
Centralized and Onchain RWA Perpetual Volume by Venue (2026 Cumulative)
소스: CoinMarketCap Research, RWA Perpetuals State of the Market (Aug 2026).
윈도우: 2025-12-29 ~ 2026-08-31, USD billions.
Notion agent HTML(16_cmc_cex_onchain_venue_volume_notion_agent_chart.html) 재현.
왼쪽 "Leading venues" 6개(값 + 점유율), 오른쪽 "Other onchain venues" 11개(자체 스케일).
CEX 블루 / DEX 그린. 타입별 단색(강조 톤 없음).
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, SERIES_COLORS, gradient_barh, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/rwa_perp_volume_by_venue.csv'

CEX, DEX = SERIES_COLORS[0], SERIES_COLORS[1]   # 블루 / 그린

TICK_FONT  = 18
VALUE_FONT = 16
SHARE_FONT = 13
BAR_HEIGHT = 0.62
GRAD_FLOOR = 0.80

LEFT_XMAX,  LEFT_TICKS  = 2000, [0, 500, 1000, 1500, 2000]
RIGHT_XMAX, RIGHT_TICKS = 60,   [0, 20, 40, 60]

OUT_NAME = 'rwa_perp_volume_by_venue'
OUT_DIR  = 'outputs/charts/rwa/perps'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
total = df['volume_busd'].sum()
lead, other = df[df.panel == 'leading'], df[df.panel == 'other']

fig, (axL, axR) = plt.subplots(1, 2, figsize=(17.0, 6.4), dpi=150,
                               gridspec_kw={'width_ratios': [1.05, 0.95], 'wspace': 0.55})
fig.patch.set_alpha(0)


def panel(ax, d, xmax, ticks, show_share):
    ax.set_facecolor('none')
    for s in ax.spines.values():
        s.set_visible(False)
    y = np.arange(len(d))
    for yi, row in zip(y, d.itertuples()):
        c = CEX if row.type == 'CEX' else DEX
        rect = ax.barh(yi, row.volume_busd, height=BAR_HEIGHT, color=c, zorder=3)[0]
        gradient_barh(ax, rect, c, floor=GRAD_FLOOR)
        label = f"${row.volume_busd:,.1f}B"
        ax.text(row.volume_busd + xmax * 0.012, yi, label, ha='left', va='center',
                color=TEXT, fontsize=VALUE_FONT, fontweight='bold', zorder=4)
        if show_share:
            ax.annotate(f"{row.volume_busd / total * 100:.1f}%", (row.volume_busd, yi),
                        xytext=(len(label) * VALUE_FONT * 0.56 + 10, 0),
                        textcoords='offset points', ha='left', va='center',
                        color=TEXT2, fontsize=SHARE_FONT, fontweight='bold', zorder=4)
    ax.set_xlim(0, xmax)
    ax.set_ylim(len(d) - 0.5, -0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(d['venue'])
    ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT, length=0, pad=12)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"${t:,.0f}B" for t in ticks])
    ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT, length=6, width=1.2, pad=8)
    ax.grid(True, axis='x', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
    ax.set_axisbelow(True)


panel(axL, lead, LEFT_XMAX, LEFT_TICKS, show_share=True)
panel(axR, other, RIGHT_XMAX, RIGHT_TICKS, show_share=False)

fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.10)
png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
print(f"total ${total:,.1f}B | top4 {lead['volume_busd'][:4].sum() / total * 100:.1f}% | "
      f"onchain ${df[df.type == 'DEX']['volume_busd'].sum():,.1f}B")
