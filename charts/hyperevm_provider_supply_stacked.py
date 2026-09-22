"""
HyperEVM Provider Supply Over Time - Stacked Percentage Area Chart
Reproducing ASXN hyperscreener "Provider Supply Over Time" view.
Data source: DefiLlama historical TVL per protocol (aggregated by provider brand)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS

df = pd.read_csv('outputs/data/hyperevm_provider_supply.csv')
df['date'] = pd.to_datetime(df['date'])

providers = ['Kinetiq', 'Hyperbeat', 'Valantis', 'Hyperdrive', 'Kintsu', 'Hyperpie']

for p in providers:
    df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)

df = df[df['date'] >= '2025-04-01'].copy().reset_index(drop=True)

row_totals = df[providers].sum(axis=1).replace(0, np.nan)
shares = df[providers].div(row_totals, axis=0).fillna(0) * 100

stack_order = ['Kinetiq', 'Hyperdrive', 'Valantis', 'Hyperbeat', 'Hyperpie', 'Kintsu']
colors = {
    'Kinetiq':    '#1e5938',
    'Hyperdrive': '#4aae8a',
    'Valantis':   '#0f3d24',
    'Hyperbeat':  '#e8ece9',
    'Hyperpie':   '#787b86',
    'Kintsu':     '#b5b9b6',
}

fig, ax = create_figure('stacked')

y_stack = np.row_stack([shares[p].values for p in stack_order])
ax.stackplot(df['date'], y_stack, colors=[colors[p] for p in stack_order], alpha=0.95, linewidth=0)

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}%'))

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max())

apply_style(fig, ax, 'stacked')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

out_dir = 'outputs/charts/hyperliquid/lst'
png, svg = save_chart(fig, 'hyperevm_provider_supply_stacked', out_dir)
plt.close(fig)
print(f'PNG: {png}')
print(f'SVG: {svg}')

latest = df.iloc[-1]
total = latest[providers].sum()
print(f'\nLatest ({latest["date"].strftime("%Y-%m-%d")}):')
for p in providers:
    v = latest[p]
    print(f'  {p}: ${v/1e6:.1f}M ({v/total*100:.2f}%)')
print(f'  TOTAL: ${total/1e6:.1f}M')
