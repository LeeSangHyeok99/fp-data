import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

setup_font()

# =============================================================================
# Data (extracted from reference: Collector Crypt monthly gross vs net revenue)
# Bars: Gross Revenue (GMV, light blue) with Net Revenue (green) overlaid at the
# base. Line: Net Margin % (right axis). Net = gross * margin (consistent).
# =============================================================================
df = pd.read_csv('outputs/data/cc_monthly_gross_net_margin.csv')
df['date'] = pd.to_datetime(df['month'])
df['net_musd'] = (df['gross_musd'] * df['net_margin_pct'] / 100).round(2)

GROSS_COLOR = '#a9d3ec'  # light blue
NET_COLOR = '#3cb46e'    # green
LINE_COLOR = '#d6452f'   # brick red

OUTPUT_DIR = 'outputs/charts/collector_crypt/revenue'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')

    x = np.arange(len(df))
    width = 0.62

    # gross (full bar) then net overlaid at base
    ax.bar(x, df['gross_musd'], width, color=GROSS_COLOR,
           edgecolor='none', zorder=2)
    ax.bar(x, df['net_musd'], width, color=NET_COLOR,
           edgecolor='none', zorder=3)

    # net margin % line (right axis)
    ax2.plot(x, df['net_margin_pct'], color=LINE_COLOR, linewidth=2.2,
             marker='o', markersize=5, zorder=5)

    # left axis: revenue $M (5 ticks)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels([f'${t}M' for t in [0, 25, 50, 75, 100]],
                       fontsize=12, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(0, 110)

    # right axis: net margin % (5 ticks, aligned to left gridlines)
    ax2.set_yticks([0, 5, 10, 15, 20])
    ax2.set_yticklabels([f'{t}%' for t in [0, 5, 10, 15, 20]],
                        fontsize=12, fontweight='bold', color=LINE_COLOR)
    ax2.set_ylim(0, 22)

    # x axis: Mon YYYY
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b %Y') for d in df['date']],
                       fontsize=10, fontweight='bold',
                       color=COLORS['text_secondary'], rotation=45, ha='right')
    ax.set_xlim(-0.7, len(df) - 0.3)

    # grid (left axis only; right ticks align to same gridlines)
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

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/cc_monthly_gross_net_margin_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((11.5, 5.5), 'wide')
print('Done: cc_monthly_gross_net_margin')
print(f"  Cumulative gross ${df['gross_musd'].sum():.0f}M | net ${df['net_musd'].sum():.1f}M"
      f" | margin {df['net_margin_pct'].iloc[0]}% -> {df['net_margin_pct'].iloc[-1]}%")
