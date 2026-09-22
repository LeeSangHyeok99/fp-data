import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

df = pd.read_csv('outputs/data/ethena_system_backing.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

series_order = ['Liquid_Stables', 'BTC', 'ETH', 'ETH_LSTs']
omitted = ['BNB', 'XRP', 'SOL']

color_map = {
    'Liquid_Stables': '#E5E7EB',
    'BTC':            '#F7931A',
    'ETH':            '#627EEA',
    'ETH_LSTs':       '#00D4B4',
}

for col in series_order:
    if col not in df.columns:
        df[col] = 0
    df[col] = df[col].fillna(0) / 1e9

total = df[series_order].sum(axis=1)
peak_value = total.max()
y_max = (int(peak_value) // 2 + 1) * 2 if peak_value > 0 else 14
y_ticks = [0, y_max / 4, y_max / 2, 3 * y_max / 4, y_max]

fig, ax = create_figure('stacked')
ax.stackplot(
    df['date'],
    *[df[c].values for c in series_order],
    colors=[color_map[c] for c in series_order],
    alpha=0.92,
    linewidth=0,
)

ax.plot(df['date'], total, color='#FFFFFF', linewidth=1.2, alpha=0.85)

ax.set_ylim(0, y_max)
ax.set_yticks(y_ticks)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'${x:.0f}B' if x == int(x) else f'${x:.1f}B'))

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max() + pd.Timedelta(days=7))

apply_style(fig, ax, 'stacked')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

png_path, svg_path = save_chart(fig, 'ethena_system_backing', 'outputs/charts/ethena/backing')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

print("\n--- Total System Backing ---")
print(f"  Start:  {df['date'].iloc[0].strftime('%Y-%m-%d')}  ${total.iloc[0]:.2f}B")
print(f"  Peak:   {df.loc[total.idxmax(), 'date'].strftime('%Y-%m-%d')}  ${peak_value:.2f}B")
print(f"  End:    {df['date'].iloc[-1].strftime('%Y-%m-%d')}  ${total.iloc[-1]:.2f}B")

print("\n--- Apr 2026 composition (plotted) ---")
latest = df.iloc[-1]
for c in series_order:
    val = latest[c]
    share = val / total.iloc[-1] * 100 if total.iloc[-1] > 0 else 0
    print(f"  {c:<16} ${val:>6.2f}B  {share:>5.1f}%")

print("\n--- Omitted (<0.3% each, raw USD) ---")
for c in omitted:
    if c in latest:
        val_usd = float(latest[c])
        share = val_usd / 1e9 / total.iloc[-1] * 100 if total.iloc[-1] > 0 else 0
        print(f"  {c:<16} ${val_usd/1e6:>6.2f}M  {share:>5.2f}%")
