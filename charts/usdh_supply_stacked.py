"""
USDH Total Supply - Stacked Area (HyperCore vs HyperEVM)
Generates both four-pillars and hrc theme versions
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, os

# ── Data ──
df = pd.read_csv('/Users/ijaheun/Desktop/USDH_Total_Supply.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

dates = df['date']
hypercore = df['supply_on_hypercore'] / 1e6  # to millions
hyperevm = df['supply_on_hyperevm'] / 1e6

# ── Shared chart logic ──
def draw_chart(config_path, theme_name, output_dir, filename):
    sys.path.insert(0, config_path)
    # Force reimport
    if 'config' in sys.modules:
        del sys.modules['config']
    from config import create_figure, apply_style, save_chart, COLORS

    # Hyperliquid green tones - HyperEVM(bottom) lighter, HyperCore(top) darker
    colors = ['#a8f0dc', '#1a8a6e']  # light mint, deep forest green

    fig, ax = create_figure('stacked')

    ax.stackplot(dates, hypercore, hyperevm,
                 colors=colors, alpha=0.85, linewidth=0.5,
                 edgecolor=COLORS.get('background', '#141414'))

    # Y axis
    max_val = (hypercore + hyperevm).max()
    tick_max = int(np.ceil(max_val / 20) * 20)
    y_ticks = np.arange(0, tick_max + 1, 20)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{int(v)}M' for v in y_ticks])
    ax.set_ylim(0, tick_max)

    # X axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

    apply_style(fig, ax, 'stacked')
    save_chart(fig, filename, output_dir)
    plt.close()
    print(f'Saved {theme_name}: {output_dir}/{filename}.png')

    sys.path.pop(0)


# ── Four Pillars ──
fp_config = os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars')
draw_chart(fp_config, 'four-pillars',
           'outputs/charts/hyperliquid/stablecoin',
           'usdh_supply_stacked_fp')

# ── HRC ──
hrc_config = os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'hrc')
draw_chart(hrc_config, 'hrc',
           'outputs/charts/hyperliquid/stablecoin',
           'usdh_supply_stacked_hrc')
