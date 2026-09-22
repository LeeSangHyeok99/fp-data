"""OnRe monthly market cap on Solana (Allium reference), purple line with area fill.

Data: outputs/data/onre_market_cap_monthly.csv, extracted from the Allium
"Market cap" chart image (Aug 2025 to Aug 2026, last point $269M).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, COLORS, DPI

setup_font()

df = pd.read_csv('outputs/data/onre_market_cap_monthly.csv', parse_dates=['date'])
LINE = '#7B2D8E'  # reference purple

OUTPUT_DIR = 'outputs/charts/onre/market_cap'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(15.0, 6.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.fill_between(df['date'], df['market_cap_musd'], color=LINE, alpha=0.15,
                linewidth=0, zorder=2)
ax.plot(df['date'], df['market_cap_musd'], color=LINE, linewidth=3.2, zorder=3,
        solid_joinstyle='round', solid_capstyle='round')

last = df.iloc[-1]
ax.annotate(f'${last.market_cap_musd:.0f}M', (last['date'], last.market_cap_musd),
            xytext=(-6, 14), textcoords='offset points', ha='right', va='bottom',
            fontsize=18, fontweight='bold', color=LINE, zorder=4)

ax.set_ylim(0, 300)
ax.set_yticks([0, 100, 200, 300])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 8, 12]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=14, length=0, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=8, rotation=45,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation_mode='anchor')
fig.tight_layout()

for fmt in ('png', 'svg'):
    fig.savefig(f'{OUTPUT_DIR}/onre_market_cap_monthly.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(f'{OUTPUT_DIR}/onre_market_cap_monthly.svg')
