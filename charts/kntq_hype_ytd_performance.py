import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import COLORS, DPI, GRID_CONFIG, setup_font


df = pd.read_csv('outputs/data/kntq_hype_ytd.csv', usecols=[0, 1, 2])
df.columns = ['date', 'kntq', 'hype']
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y')
df = df.sort_values('date').reset_index(drop=True)

base_kntq = df['kntq'].iloc[0]
base_hype = df['hype'].iloc[0]
df['kntq_pct'] = (df['kntq'] / base_kntq - 1) * 100
df['hype_pct'] = (df['hype'] / base_hype - 1) * 100

KNTQ_COLOR = '#1e5695'
HYPE_COLOR = '#e8984a'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.plot(df['date'], df['kntq_pct'], color=KNTQ_COLOR, linewidth=2.0, zorder=4)
ax.plot(df['date'], df['hype_pct'], color=HYPE_COLOR, linewidth=2.0, zorder=3)

ax.set_ylim(-50, 400)
y_ticks = [0, 100, 200, 300, 400]
ax.yaxis.set_major_locator(mticker.FixedLocator(y_ticks))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v)}%'))

ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.grid(axis='x', visible=False)
ax.axhline(0, color=COLORS['text_secondary'], linewidth=0.8, alpha=0.5, zorder=1)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=14, pad=10, length=0, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=13, pad=10, length=0, colors=COLORS['text_secondary'])
for lbl in ax.get_xticklabels():
    lbl.set_fontweight('bold')
for lbl in ax.get_yticklabels():
    lbl.set_fontweight('bold')

fig.tight_layout()

out_dir = Path('outputs/charts/kinetiq/token')
out_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(out_dir / 'kntq_hype_ytd_performance.png',
            dpi=DPI, facecolor='none', transparent=True, bbox_inches='tight')
fig.savefig(out_dir / 'kntq_hype_ytd_performance.svg',
            dpi=DPI, facecolor='none', transparent=True, bbox_inches='tight', format='svg')
plt.close(fig)

peak_idx = df['kntq_pct'].idxmax()
last = df.iloc[-1]
print(f"Saved to {out_dir}/")
print(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"KNTQ peak: {df['kntq_pct'].max():.2f}% on {df.iloc[peak_idx]['date'].date()}")
print(f"Last ({last['date'].date()}): KNTQ {last['kntq_pct']:.2f}%, HYPE {last['hype_pct']:.2f}%")
print(f"HYPE - KNTQ gap (last): {last['hype_pct'] - last['kntq_pct']:.2f} pp")
