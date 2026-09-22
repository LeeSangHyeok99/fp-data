"""Total RWA Value by asset class, last 2 years (stacked area).

Reproduces app.rwa.xyz/overview "Total RWA Value" (Distributed, Total Value,
stablecoins excluded), keeping every asset class from the reference legend.

Data: sources/rwa-token-timeseries-export-1788252801943.csv (rwa.xyz export)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, band_gradient

setup_font()

SRC = 'sources/rwa-token-timeseries-export-1788252801943.csv'
CSV = 'outputs/data/rwa_total_value_by_asset_class.csv'

# colors read off the rwa.xyz legend
ASSET_COLORS = {
    'US Treasury Debt':       '#14356b',
    'Commodities':            '#c9a13b',
    'Active Strategies':      '#4a7fa8',
    'Stocks':                 '#f4402a',
    'Asset-Backed Credit':    '#5f7f2b',
    'Specialty Finance':      '#c2185b',
    'Corporate Credit':       '#7b3fe4',
    'Private Equity':         '#f5c518',
    'non-US Government Debt': '#a9c2d9',
    'Venture Capital':        '#a8e0a0',
    'Diversified Credit':     '#1a2ff0',
    'Real Estate':            '#b8551e',
    # Public Equity / Municipal Credit are in the rwa.xyz legend but carry no
    # value in this window ($373K peak / $2.4K peak), so they are not stacked.
}

if Path(SRC).exists():  # refresh the chart CSV from the rwa.xyz export
    raw = pd.read_csv(SRC)
    raw['Date'] = pd.to_datetime(raw['Date'])
    raw = raw[raw['Date'] >= raw['Date'].max() - pd.DateOffset(years=2)]
    v = raw[list(ASSET_COLORS)].apply(pd.to_numeric, errors='coerce').fillna(0) / 1e9
    out = v[v.iloc[-1].sort_values(ascending=False).index]  # largest class first
    out.insert(0, 'Date', raw['Date'].dt.date)
    out['Total'] = v.sum(axis=1)
    out.round(6).to_csv(CSV, index=False)

df = pd.read_csv(CSV, parse_dates=['Date'])
vals = df[list(ASSET_COLORS)]
# stack smallest at the bottom, largest on top (matches the reference layout)
order = vals.iloc[-1].sort_values().index.tolist()

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

xnum = mdates.date2num(df['Date'])
lower = pd.Series(0.0, index=df.index)
for c in order:
    upper = lower + vals[c]
    band_gradient(ax, xnum, lower.to_numpy(), upper.to_numpy(), ASSET_COLORS[c],
                  spread=0.12)
    lower = upper

ticks = [0, 10, 20, 30, 40]
ax.set_yticks(ticks)
ax.set_yticklabels([f'${t}B' for t in ticks], fontsize=16, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.set_ylim(0, 42)
ax.set_xlim(df['Date'].min(), df['Date'].max())

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x', labelsize=12, rotation=45, length=6, width=1,
               colors=COLORS['text_secondary'])
for lbl in ax.xaxis.get_majorticklabels():
    lbl.set_ha('right')
    lbl.set_fontweight('bold')
    lbl.set_color(COLORS['text'])

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', length=0)

OUT = Path('outputs/charts/rwa/overview')
OUT.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(OUT / f'total_rwa_value_by_asset_class_wide.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)

tot = vals.sum(axis=1)
print(f'{df["Date"].min().date()} ~ {df["Date"].max().date()}')
print(f'  total ${tot.iloc[0]:.2f}B -> ${tot.iloc[-1]:.2f}B ({tot.iloc[-1]/tot.iloc[0]-1:+.0%})')
print('  stack bottom -> top:', ', '.join(order))
