"""
JPYC Cumulative Issuance by Chain - Stacked Area (four-pillars)
Source: Dune (@JPYCダッシュボード), daily mint per chain -> cumulative issuance
Data: /Users/a./Downloads/test (1).csv  (date, blockchain, mint_amount)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, os

# ── Data: daily mint per chain -> pivot -> cumulative ──
src = '/Users/a./Downloads/test (1).csv'
df = pd.read_csv(src)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

pivot = df.pivot_table(index='date', columns='blockchain',
                       values='mint_amount', aggfunc='sum').fillna(0)
pivot = pivot.sort_index()
cum = pivot.cumsum()

# Persist prepared data
prep = cum.copy()
prep_path = 'outputs/data/jpyc_cumulative_issuance_by_chain.csv'
os.makedirs('outputs/data', exist_ok=True)
prep.to_csv(prep_path)
print(f'Saved data: {prep_path}  (total ¥{cum.iloc[-1].sum():,.0f})')

dates = cum.index

# Stack order bottom -> top (matches reference): Avalanche, Polygon, Ethereum, Kaia
order = ['avalanche', 'polygon', 'ethereum', 'kaia']
# Chain brand-aligned colors matching the reference infographic
chain_colors = {
    'avalanche': '#e84142',  # Avalanche red
    'polygon':   '#8247e5',  # Polygon purple
    'ethereum':  '#73c0de',  # light blue
    'kaia':      '#b6e94a',  # lime green
}
series = [cum[c].values for c in order]
colors = [chain_colors[c] for c in order]


def draw_chart(config_path, output_dir, filename):
    sys.path.insert(0, config_path)
    if 'config' in sys.modules:
        del sys.modules['config']
    from config import create_figure, apply_style, save_chart, COLORS

    fig, ax = create_figure('stacked')

    ax.stackplot(dates, *series, colors=colors, alpha=0.9,
                 linewidth=0.5, edgecolor=COLORS.get('background', '#141414'))

    # Y axis: yen, ticks at 0..4B
    y_ticks = np.arange(0, 4.0e9 + 1, 1.0e9)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'¥{int(v/1e9)}B' for v in y_ticks])
    ax.set_ylim(0, 4.0e9)

    # X axis: monthly, Mon YYYY, no side padding
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.set_xlim(dates.min(), dates.max())

    apply_style(fig, ax, 'stacked')
    png, svg = save_chart(fig, filename, output_dir)
    plt.close()
    print(f'Saved chart: {png}')
    sys.path.pop(0)


fp_config = os.path.join(os.path.dirname(__file__), '..', '.claude',
                         'skills', 'design', 'four-pillars')
draw_chart(fp_config, 'outputs/charts/jpyc/issuance',
           'jpyc_cumulative_issuance_stacked_fp')
