"""
HYPE ETF Cumulative Inflows vs HYPE Price (YTD 2026)
Dual-axis chart, Four Pillars theme.

Left axis  : Cumulative HYPE spot-ETF net inflows ($M), launch 2026-05-12
Right axis : HYPE spot price ($), full YTD

Data:
  - ETF flows: farside.co.uk/hyp/ (BHYP Bitwise + THYP 21Shares).
    Cross-checked: cumulative $145.1M == Farside Total row (145).
  - HYPE price: CoinGecko (coin id "hyperliquid"), via hip3 YTD CSV.
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
END_DATE = etf['date'].iloc[-1]
# Align both lines to the same right edge (ETF flow's last data point).
price = df[df['date'] <= END_DATE].copy()


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

    # ─── Right axis: HYPE price (trimmed to align with ETF line) ───
    axr.plot(price['date'], price['hype_price_usd'], color=COLOR_PRICE,
             linewidth=2.6, zorder=4, alpha=0.95)

    # ─── Endpoint dots (clip_on=False so edge dots stay whole) ─────
    last = price.iloc[-1]
    ax.scatter(etf['date'].iloc[-1], etf['cum_inflow_m'].iloc[-1],
               color=COLOR_FLOW, s=70, zorder=6, edgecolors='none', clip_on=False)
    axr.scatter(last['date'], last['hype_price_usd'],
                color=COLOR_PRICE, s=70, zorder=6, edgecolors='none', clip_on=False)

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

    # ─── X axis (zoom to ETF launch window for like-for-like compare) ─
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=0)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='center', fontweight='bold')
    ax.set_xlim(etf['date'].iloc[0], END_DATE)

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
    # Reserve right margin so bold right-axis labels ($80…) aren't clipped at
    # the viewBox edge by SVG renderers that use wider fallback font metrics.
    axr.text(1.045, 0.5, '$80', transform=axr.transAxes,
             fontsize=18, fontweight='bold', alpha=0, ha='left', va='center')
    return fig


if __name__ == '__main__':
    print('Drawing hype_etf_inflows_vs_price_ytd (Four Pillars)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hype_etf_inflows_vs_price_ytd', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
