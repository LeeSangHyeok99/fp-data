"""
HIP-3 14d / 30d Moving-Average Daily Volume vs HYPE Price (YTD 2026)
Dual-axis line chart, HRC theme.

Left axis  : HIP-3 builder-deployed perp daily volume, 14d & 30d moving avg ($B)
Right axis : HYPE spot price ($)

Data:
  - HIP-3 volume: ASXN Hyperscreener (api-hyperliquid.asxn.xyz
    /api/meta/hip3/stacked-volume-chart?timeperiod=all), daily total_volume
    summed across all builder-deployers.
    -> outputs/data/hip3_ma_volume_vs_hype_ytd.csv
  - HYPE price: CoinGecko market_chart (coin id "hyperliquid").
    -> outputs/data/hype-usd-max.csv (snapped_at, price)
"""

import sys
sys.path.insert(0, '.claude/skills/design/hrc')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

# keep axis text as editable <text> in SVG (not vector paths)
plt.rcParams['svg.fonttype'] = 'none'

OUTPUT_DIR = 'outputs/charts/hyperliquid/hip3'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Colors ──────────────────────────────────────────────────────────────
COLOR_MA14 = '#50e3c2'   # Hyperliquid teal  → HIP-3 14d MA
COLOR_MA30 = '#7c3aed'   # Electric purple   → HIP-3 30d MA
COLOR_HYPE = '#f59e0b'   # Amber             → HYPE price (right axis)

# ─── Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_ma_volume_vs_hype_ytd.csv', parse_dates=['date'])
df['ma14_B'] = df['hip3_vol_ma14'] / 1e9
df['ma30_B'] = df['hip3_vol_ma30'] / 1e9

# HYPE price from CoinGecko export (hype-usd-max.csv)
hype = pd.read_csv('outputs/data/hype-usd-max.csv')
hype['date'] = pd.to_datetime(
    hype['snapped_at'].str.replace(' UTC', '', regex=False)).dt.normalize()
hype = hype[['date', 'price']].rename(columns={'price': 'hype_price_usd'})
df = df.drop(columns=['hype_price_usd']).merge(hype, on='date', how='left')


def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(12, 5), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    axr = ax.twinx()
    axr.set_facecolor('none')

    # ─── Left axis: HIP-3 MA volume ────────────────────────────────
    ax.plot(df['date'], df['ma30_B'], color=COLOR_MA30,
            linewidth=2.6, zorder=4, alpha=0.95)
    ax.plot(df['date'], df['ma14_B'], color=COLOR_MA14,
            linewidth=2.8, zorder=5)
    ax.fill_between(df['date'], 0, df['ma14_B'],
                    color=COLOR_MA14, alpha=0.07, zorder=2)

    # ─── Right axis: HYPE price ────────────────────────────────────
    axr.plot(df['date'], df['hype_price_usd'], color=COLOR_HYPE,
             linewidth=2.6, zorder=6, alpha=0.95)

    # ─── Endpoint dots ─────────────────────────────────────────────
    last = df.iloc[-1]
    ax.scatter(last['date'], last['ma14_B'], color=COLOR_MA14, s=70,
               zorder=7, edgecolors='white', linewidth=1.5)
    ax.scatter(last['date'], last['ma30_B'], color=COLOR_MA30, s=70,
               zorder=7, edgecolors='white', linewidth=1.5)
    axr.scatter(last['date'], last['hype_price_usd'], color=COLOR_HYPE, s=70,
                zorder=8, edgecolors='white', linewidth=1.5)

    # ─── Left Y axis (volume, 4 ticks) ─────────────────────────────
    ax.set_ylim(0, 3)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 1, 2, 3]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'${v:.0f}B'))
    ax.tick_params(axis='y', labelsize=18, pad=12, length=0,
                   colors=COLOR_MA14)
    for lb in ax.get_yticklabels():
        lb.set_fontweight('bold')

    # ─── Right Y axis (HYPE price, 4 ticks) ────────────────────────
    axr.set_ylim(0, 75)
    axr.yaxis.set_major_locator(mticker.FixedLocator([0, 25, 50, 75]))
    axr.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f'${v:.0f}'))
    axr.tick_params(axis='y', labelsize=18, pad=12, length=0,
                    colors=COLOR_HYPE)
    for lb in axr.get_yticklabels():
        lb.set_fontweight('bold')

    # ─── X axis ────────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=0)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='center', fontweight='bold')
    # small right pad so endpoint dots aren't clipped
    span = df['date'].iloc[-1] - df['date'].iloc[0]
    ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1] + span * 0.01)

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
    print('Drawing hip3_ma_volume_vs_hype_ytd (HRC)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hip3_ma_volume_vs_hype_ytd', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
