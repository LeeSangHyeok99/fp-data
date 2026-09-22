"""
HYPE 14d / 30d P/E Ratio (Market Cap / Annualized Buybacks), YTD 2026
Single-axis line chart, HRC theme.

P/E = HYPE market cap / annualized Assistance Fund buyback run-rate
  - 14d line: market cap / (14d MA daily buyback x 365)
  - 30d line: market cap / (30d MA daily buyback x 365)

Data:
  - Buybacks: ASXN api-data.asxn.xyz/api/data/hl-buybacks (daily notional USD).
    Cross-checked vs DefiLlama Hyperliquid daily revenue (buyback/rev = 0.86 YTD).
  - Market cap: CoinGecko market_chart (coin id "hyperliquid").
Source CSV: outputs/data/hype_pe_buyback_ytd.csv
"""

import sys
sys.path.insert(0, '.claude/skills/design/hrc')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from pathlib import Path
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

# keep axis text as editable <text> in SVG (SUIT), not baked-in vector paths
plt.rcParams['svg.fonttype'] = 'none'

# Heaviest SUIT weight for thick, legible axis labels (setup_font only loads Bold)
_HEAVY_PATH = Path('assets/font/SUIT/SUIT-ttf/SUIT-Heavy.ttf')
if _HEAVY_PATH.exists():
    fm.fontManager.addfont(str(_HEAVY_PATH))
# reference by family name (not fname) so SVG fonttype='none' emits font-family:'SUIT'
TICK_FONT = fm.FontProperties(family='SUIT', weight='heavy') if _HEAVY_PATH.exists() else None

OUTPUT_DIR = 'outputs/charts/hyperliquid/revenue'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ─── Colors ──────────────────────────────────────────────────────────────
COLOR_PE14 = '#50e3c2'   # Hyperliquid teal  → 14d P/E
COLOR_PE30 = '#7c3aed'   # Electric purple   → 30d P/E

# ─── Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hype_pe_buyback_ytd.csv', parse_dates=['date'])


def draw_chart():
    setup_font()
    fig, ax = plt.subplots(figsize=(15, 6.25), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # ─── P/E lines ─────────────────────────────────────────────────
    ax.plot(df['date'], df['pe_30d'], color=COLOR_PE30,
            linewidth=2.6, zorder=4, alpha=0.95)
    ax.plot(df['date'], df['pe_14d'], color=COLOR_PE14,
            linewidth=2.8, zorder=5)
    ax.fill_between(df['date'], 0, df['pe_14d'],
                    color=COLOR_PE14, alpha=0.07, zorder=2)

    # ─── Endpoint dots ─────────────────────────────────────────────
    last = df.iloc[-1]
    ax.scatter(last['date'], last['pe_14d'], color=COLOR_PE14, s=70,
               zorder=7, edgecolors='white', linewidth=1.5, clip_on=False)
    ax.scatter(last['date'], last['pe_30d'], color=COLOR_PE30, s=70,
               zorder=7, edgecolors='white', linewidth=1.5, clip_on=False)

    # ─── Y axis (P/E, 4 ticks) ─────────────────────────────────────
    ax.set_ylim(0, 32)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f}x'))
    ax.tick_params(axis='y', labelsize=26, pad=12, length=0,
                   colors=COLORS['text_secondary'])
    for lb in ax.get_yticklabels():
        if TICK_FONT:
            lb.set_fontproperties(TICK_FONT)
        lb.set_fontsize(26)

    # ─── X axis ────────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=22, pad=10, length=0,
                   colors=COLORS['text_secondary'], rotation=45)
    for lb in ax.get_xticklabels():
        if TICK_FONT:
            lb.set_fontproperties(TICK_FONT)
        lb.set_fontsize(22)
        lb.set_ha('right')
    ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1])

    # ─── Grid ──────────────────────────────────────────────────────
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    print('Drawing hype_pe_buyback_ytd (HRC)...')
    fig = draw_chart()
    png, svg = save_chart(fig, 'hype_pe_buyback_ytd', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
    print('Done.')
