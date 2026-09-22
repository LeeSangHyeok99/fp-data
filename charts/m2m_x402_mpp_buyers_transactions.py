import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

setup_font()

# =============================================================================
# M2M (x402 + MPP) Ecosystem: Buyers (stacked bars, left) + Transactions
# (2 lines, right). Weekly (week ending Sunday), 2026-05-31 -> 2026-06-21.
#   Source: Artemis daily CSV export (classic.artemis.ai/asset/x402, /mpp).
#   Weekly aggregation reproduces Artemis tooltips exactly:
#     Transactions = weekly SUM, Buyers = weekly daily-AVG.
#   Validated: w/e May 31 -> x402 773.9K tx / 7.6K buyers, MPP 165.5K / 2.6K.
#   Protocols distinguished by color: x402 = blue, MPP = orange.
# =============================================================================
df = pd.read_csv('outputs/data/m2m_x402_mpp_weekly.csv')
weeks = pd.to_datetime(df['week_ending'])
n = len(df)
x = np.arange(n, dtype=float)

X402 = '#4d7cfe'   # x402 (blue)
MPP = '#f5a623'    # MPP (orange)

OUTPUT_DIR = 'outputs/charts/platform/m2m'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')

    width = 0.55
    # buyers: stacked bars (left axis), x402 bottom + MPP on top
    ax.bar(x, df['x402_buyers'], width=width, color=X402, zorder=2, linewidth=0)
    ax.bar(x, df['mpp_buyers'], width=width, bottom=df['x402_buyers'],
           color=MPP, zorder=2, linewidth=0)

    # transactions: 2 lines (right axis), raw counts (axis ticks labeled in M).
    # White halo (path effect) so the lines stay legible over same-color bars.
    halo = [pe.Stroke(linewidth=5.5, foreground='white'), pe.Normal()]
    ax2.plot(x, df['x402_transactions'], color=X402, linewidth=2.8,
             zorder=6, marker='o', markersize=8, markeredgecolor='white',
             markeredgewidth=1.6, solid_capstyle='round', path_effects=halo)
    ax2.plot(x, df['mpp_transactions'], color=MPP, linewidth=2.8,
             zorder=6, marker='o', markersize=8, markeredgecolor='white',
             markeredgewidth=1.6, solid_capstyle='round', path_effects=halo)

    # left axis: Buyers (5 ticks, K)
    ax.set_yticks([0, 3000, 6000, 9000, 12000])
    ax.set_yticklabels(['0K', '3K', '6K', '9K', '12K'], fontsize=13,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 15000)

    # right axis: Transactions (5 ticks, M, aligned to left gridlines)
    ax2.set_yticks([0, 1e6, 2e6, 3e6, 4e6])
    ax2.set_yticklabels(['0M', '1M', '2M', '3M', '4M'], fontsize=13,
                        fontweight='bold', color=COLORS['text_secondary'])
    ax2.set_ylim(0, 5e6)

    # x axis: weekly "Mon DD" (week ending Sunday)
    ax.set_xticks(x)
    ax.set_xticklabels([w.strftime('%b %d') for w in weeks], fontsize=13,
                       fontweight='bold', color=COLORS['text'])
    ax.set_xlim(-0.6, n - 0.4)

    # grid
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)
    ax2.tick_params(axis='both', length=0)

    # legend (explicitly requested): color = protocol, shape = metric
    handles = [
        Patch(facecolor=X402, label='x402 Buyers'),
        Patch(facecolor=MPP, label='MPP Buyers'),
        Line2D([0], [0], color=X402, lw=2.8, marker='o', markersize=8,
               markeredgecolor='white', markeredgewidth=1.6,
               label='x402 Transactions'),
        Line2D([0], [0], color=MPP, lw=2.8, marker='o', markersize=8,
               markeredgecolor='white', markeredgewidth=1.6,
               label='MPP Transactions'),
    ]
    leg = ax.legend(handles=handles, loc='lower left',
                    bbox_to_anchor=(0.0, 1.01, 1.0, 0.12), mode='expand',
                    ncol=4, frameon=False, fontsize=11.5,
                    labelcolor=COLORS['text'], handlelength=1.6,
                    columnspacing=1.2, handletextpad=0.5)
    for t in leg.get_texts():
        t.set_fontweight('bold')

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/m2m_x402_mpp_buyers_transactions_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.2), 'wide')
print('Done: m2m_x402_mpp_buyers_transactions (REAL weekly data)')
for _, r in df.iterrows():
    print(f"  {r['week_ending']}: x402 tx={r['x402_transactions']/1e6:.2f}M "
          f"buy={r['x402_buyers']/1e3:.1f}K | MPP tx={r['mpp_transactions']/1e3:.0f}K "
          f"buy={r['mpp_buyers']/1e3:.1f}K")
