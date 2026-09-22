import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Data: Ondo Perps daily open interest (DefiLlama open-interest API)
# =============================================================================
from numbers_parser import Document

rows = Document('sources/ondo_oi_daily.numbers').sheets[0].tables[0].rows(values_only=True)
df = pd.DataFrame(rows[1:], columns=rows[0])
df['date'] = pd.to_datetime(df['date'])
df['oi'] = df['open_interest_usd'].astype(float) / 1e6
df = df.sort_values('date').reset_index(drop=True)

LAUNCH = pd.Timestamp('2026-07-07')   # public launch
EARLY = df['date'].iloc[0]            # early access (2026-06-09)
peak = df.loc[df['oi'].idxmax()]
last = df.iloc[-1]

LINE = '#3aa6b9'
PEAK = '#e0803f'

# =============================================================================
# Chart
# =============================================================================
fig, ax = create_figure('line')
ax.fill_between(df['date'], df['oi'], color=LINE, alpha=0.16, linewidth=0, zorder=2)
ax.plot(df['date'], df['oi'], color=LINE, linewidth=2.2, zorder=3)

# 공개 런칭 구분선
ax.axvline(LAUNCH, color='#787b86', linestyle=(0, (2, 2)), linewidth=1.0, zorder=1)
ax.text(LAUNCH + pd.Timedelta(days=1), 46, 'Public Launch\nJul 7', ha='left', va='center',
        fontsize=13, fontweight='bold', color='#787b86', zorder=4)
ax.text(EARLY + pd.Timedelta(days=1), 46, 'Early Access\nJun 9', ha='left', va='center',
        fontsize=13, fontweight='bold', color='#787b86', zorder=4)

# 피크 / 최신
ax.scatter([peak['date']], [peak['oi']], s=45, color=PEAK, zorder=5, edgecolors='none')
ax.annotate(f"{peak['date']:%b %-d} Peak ${peak['oi']:.1f}M",
            xy=(peak['date'], peak['oi']), xytext=(-6, 14), textcoords='offset points',
            ha='right', va='bottom', fontsize=14, fontweight='bold', color=PEAK, zorder=6)
ax.scatter([last['date']], [last['oi']], s=45, color=LINE, zorder=5, edgecolors='none')
ax.annotate(f"{last['date']:%b %-d} ${last['oi']:.1f}M",
            xy=(last['date'], last['oi']), xytext=(-6, -20), textcoords='offset points',
            ha='right', va='top', fontsize=14, fontweight='bold', color='#d1d4dc', zorder=6)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:.0f}M'))
ax.set_ylim(0, 112)
ax.set_yticks([0, 25, 50, 75, 100])

ax.xaxis.set_major_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max())

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

out = 'outputs/charts/ondo/perps'
Path(out).mkdir(parents=True, exist_ok=True)
name = 'ondo_perps_open_interest'
fig.savefig(f'{out}/{name}.png', dpi=DPI, bbox_inches='tight', transparent=True)
fig.savefig(f'{out}/{name}.svg', format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

df[['date', 'oi']].to_csv('outputs/data/ondo_perps_open_interest.csv', index=False)

first_launch = df.loc[df['date'] == LAUNCH, 'oi'].iloc[0]
print(f"Saved: {out}/{name}.png")
print(f"Range: {df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d} ({len(df)} days)")
print(f"Launch (Jul 7): ${first_launch:.1f}M -> latest ${last['oi']:.1f}M  ({last['oi']/first_launch:.1f}x)")
print(f"Peak: ${peak['oi']:.1f}M ({peak['date']:%Y-%m-%d})")
crossed = df[df['oi'] >= 100]
print(f"First $100M cross: {crossed['date'].iloc[0]:%Y-%m-%d}" if len(crossed) else "Never crossed $100M")
