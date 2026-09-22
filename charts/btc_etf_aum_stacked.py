import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter, MonthLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Load data
# =============================================================================
flow = pd.read_csv('outputs/data/farside_btc_etf_flow.csv', parse_dates=['Date'])
price = pd.read_csv('outputs/data/btc_daily_close.csv', parse_dates=['date'])
price = price.rename(columns={'date': 'Date', 'close': 'BTC_PRICE'})

# Merge, use forward-fill to align BTC price with weekday-only flow dates
df = pd.merge(flow, price, on='Date', how='left')
df['BTC_PRICE'] = df['BTC_PRICE'].ffill().bfill()
df = df.sort_values('Date').reset_index(drop=True)

# Series: top 5 + "6 Others" (TheBlock labels 5 top + "6 Others" = 11 total ETFs)
top5 = ['IBIT', 'FBTC', 'GBTC', 'BITB', 'ARKB']
others_cols = ['BTCO', 'EZBC', 'BRRR', 'HODL', 'BTCW', 'MSBT', 'BTC']  # 7 listed incl. Grayscale BTC Mini
df['Others'] = df[others_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)

# Convert flow $m -> $
for c in top5 + ['Others']:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0) * 1e6

# BTC holdings per ETF: cumulative (flow_usd / btc_price) day-by-day
# GBTC started as a trust conversion on 2024-01-11 with ~619,220 BTC
INITIAL_BTC = {
    'IBIT': 0,
    'FBTC': 0,
    'GBTC': 619220,
    'BITB': 0,
    'ARKB': 0,
    'Others': 0,
}
series = top5 + ['Others']
for c in series:
    df[f'{c}_BTC'] = INITIAL_BTC[c] + (df[c] / df['BTC_PRICE']).cumsum()
    df[f'{c}_AUM'] = df[f'{c}_BTC'].clip(lower=0) * df['BTC_PRICE']

# AUM in $B
aum = pd.DataFrame({'Date': df['Date']})
for c in series:
    aum[c] = df[f'{c}_AUM'] / 1e9  # $B

# Clip negatives to 0 (early GBTC outflows can cause transient negative stacks when price varies)
for c in series:
    aum[c] = aum[c].clip(lower=0)

# =============================================================================
# Chart (stacked area)
# =============================================================================
fig, ax = create_figure('stacked')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Colors: matching TheBlock palette (dark blue -> light blue -> peach -> orange -> red)
colors = [
    '#1f3a8a',  # IBIT - darkest navy
    '#2f6bff',  # FBTC - blue
    '#6aa3ff',  # GBTC - light blue
    '#f4b99a',  # BITB - peach
    '#ef7a55',  # ARKB - orange
    '#b8412e',  # 6 Others - dark red/orange
]

labels = ['IBIT', 'FBTC', 'GBTC', 'BITB', 'ARKB', '6 Others']
values = [aum[c].values for c in series]

ax.stackplot(aum['Date'], *values, colors=colors, linewidth=0, zorder=2)

# Y-axis: $B
def billions_formatter(x, pos):
    return f'${x:.0f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.set_ylim(0, 200)
ax.set_yticks([0, 50, 100, 150, 200])

# X-axis: Mon YYYY, every ~4-6 months
ax.xaxis.set_major_locator(MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
ax.set_xlim(aum['Date'].min(), aum['Date'].max())

# Style
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Save
output_dir = 'outputs/charts/bitcoin/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/btc_etf_aum_stacked.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/btc_etf_aum_stacked.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/btc_etf_aum_stacked.png")

# =============================================================================
# Stats
# =============================================================================
latest = aum.iloc[-1]
total_latest = sum(latest[c] for c in series)
peak_idx = aum[series].sum(axis=1).idxmax()
peak_total = aum.loc[peak_idx, series].sum()
peak_date = aum.loc[peak_idx, 'Date']

print(f"\n--- Spot BTC ETF AUM ---")
print(f"Range: {aum['Date'].min().date()} ~ {aum['Date'].max().date()}")
print(f"Latest total AUM: ${total_latest:.1f}B ({aum['Date'].iloc[-1].date()})")
print(f"Peak total AUM:   ${peak_total:.1f}B ({peak_date.date()})")
print(f"\nLatest breakdown:")
for c in series:
    print(f"  {c:8s}: ${latest[c]:6.1f}B  ({latest[c]/total_latest*100:.1f}%)")

aum.to_csv('outputs/data/btc_etf_aum_daily.csv', index=False)
print(f"\nData saved: outputs/data/btc_etf_aum_daily.csv")
