"""
HYPE ETF Cumulative Inflows vs HYPE Price (FULL YTD 2026, Jan 1 start)
Dual-axis chart, Four Pillars theme.

Same data/axes as hype_etf_inflows_vs_price_ytd.py, but the x-axis shows the
full year-to-date window (2026-01-01 onward). The ETF inflow line only begins
at the 2026-05-12 launch; HYPE price runs the whole period.

Source CSV: outputs/data/hype_etf_inflows_vs_price_ytd.csv
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import (setup_font, save_chart, COLORS, DPI, GRID_CONFIG,
                    area_glow, endpoint_dot)

OUTPUT_DIR = 'outputs/charts/hyperliquid/etf'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Colors ──────────────────────────────────────────────────────────────
COLOR_PRICE = '#50e3c2'   # Hyperliquid teal  → HYPE price (right axis)
COLOR_FLOW  = '#f59e0b'   # Amber             → cumulative ETF inflow (left)

# ─── Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hype_etf_inflows_vs_price_ytd.csv', parse_dates=['date'])
etf = df[df['cum_inflow_m'].notna()].copy()


def draw_chart():
    setup_font()
    # hrc 스타일: SUIT 폰트로 강제
    import matplotlib.font_manager as fm
    _suit = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
    if _suit.exists():
        fm.fontManager.addfont(str(_suit))
        plt.rcParams['font.family'] = 'SUIT'
        plt.rcParams['font.weight'] = 'bold'
    fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    axr = ax.twinx()
    axr.set_facecolor('none')

    # ─── Left axis: cumulative ETF inflow ($M) ─────────────────────
    area_glow(ax, etf['date'], etf['cum_inflow_m'], color=COLOR_FLOW)
    ax.plot(etf['date'], etf['cum_inflow_m'], color=COLOR_FLOW,
            linewidth=2.8, zorder=5)

    # ─── Right axis: HYPE price (full YTD) ─────────────────────────
    axr.plot(df['date'], df['hype_price_usd'], color=COLOR_PRICE,
             linewidth=2.6, zorder=4, alpha=0.95)

    # ─── Endpoint dots ─────────────────────────────────────────────
    last = df.iloc[-1]
    endpoint_dot(ax, etf['date'].iloc[-1], etf['cum_inflow_m'].iloc[-1],
                 color=COLOR_FLOW, size=70)
    endpoint_dot(axr, last['date'], last['hype_price_usd'],
                 color=COLOR_PRICE, size=70)

    # ─── Left Y axis (cumulative inflow, 5 ticks) ──────────────────
    ax.set_ylim(0, 160)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 40, 80, 120, 160]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}M'))
    ax.tick_params(axis='y', labelsize=18, pad=12, length=0, colors=COLOR_FLOW)
    for lb in ax.get_yticklabels():
        lb.set_fontweight('bold')

    # ─── Right Y axis (HYPE price, 5 ticks) ────────────────────────
    axr.set_ylim(0, 80)
    axr.yaxis.set_major_locator(mticker.FixedLocator([0, 20, 40, 60, 80]))
    axr.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}'))
    axr.tick_params(axis='y', labelsize=18, pad=12, length=0, colors=COLOR_PRICE)
    for lb in axr.get_yticklabels():
        lb.set_fontweight('bold')

    # ─── X axis (full YTD, monthly) ────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right', fontweight='bold')
    ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1])

    # ─── Grid (left axis only) ─────────────────────────────────────
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in axr.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing hype_etf_inflows_vs_price_ytd_full (Four Pillars)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hype_etf_inflows_vs_price_ytd_full', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
