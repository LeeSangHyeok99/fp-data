import json
import sys
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

SRC = 'sources/hyperliquid-q2-data/hleco/streams_decoded/decoded__hype-etf-flows.json'
END = '2026-06-30'

flows = pd.DataFrame([{'date': r['date'], 'net_musd': r['total']}
                      for r in json.load(open(SRC))[0]['payload']['series']])
flows['date'] = pd.to_datetime(flows['date'])
cum = flows.sort_values('date').set_index('date')['net_musd'].cumsum()[:END]

MINT = '#50e3c2'
TEXT = '#ffffff'
TICK = '#747474'

# 상장일과 라벨을 놓을 높이 (곡선과 겹치지 않게 손으로 잡음)
LISTINGS = [('THYP Lists', '2026-05-12', 55), ('BHYP Lists', '2026-05-15', 105),
            ('HYPG Lists', '2026-06-03', 215)]

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 350)
ax.set_yticks([0, 100, 200, 300])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(cum.index[0], cum.index[-1])
ax.set_xticks(pd.to_datetime(['2026-05-15', '2026-06-01', '2026-06-15', '2026-06-30']))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=20, length=0, colors=TICK, pad=12)
ax.tick_params(axis='x', labelsize=18, length=6, width=1, pad=8, rotation=45,
               colors=TICK)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

ax.fill_between(cum.index, 0, cum.values, color=MINT, alpha=0.16, linewidth=0, zorder=2)
ax.plot(cum.index, cum.values, color=MINT, linewidth=2.2, zorder=3)

# 상장일 주석. 라벨에서 곡선까지 얇은 세로 리더선
for label, day, y in LISTINGS:
    d = pd.Timestamp(day)
    ax.plot([d, d], [cum.loc[d] + 6, y - 6], color=TICK, linewidth=1.2, zorder=4)
    ax.text(d, y, label, color=TEXT, fontsize=14, fontweight='bold',
            ha='center', va='bottom', zorder=5)

# 틱마크가 허공에 뜨지 않게 하단 축선을 살린다
ax.spines['bottom'].set_visible(True)
ax.spines['bottom'].set_color(TICK)
ax.spines['bottom'].set_alpha(0.6)
ax.spines['bottom'].set_linewidth(1)

ax.scatter(cum.index[-1], cum.iloc[-1], color=MINT, s=50, zorder=5, edgecolors='none')
ax.text(cum.index[-1], cum.iloc[-1] + 14, f'${cum.iloc[-1]:.0f}M', color=TEXT,
        fontsize=17, fontweight='bold', ha='right', va='bottom', zorder=5)

out = 'outputs/charts/hyperliquid/token'
Path(out).mkdir(parents=True, exist_ok=True)
cum.round(2).rename('cum_net_inflow_musd').to_csv(
    'outputs/data/hleco_hype_etf_cum_inflows.csv', index_label='date')
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_hype_etf_cum_inflows.{ext}', dpi=DPI, facecolor='none',
                edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f'{cum.index[0].date()} ~ {cum.index[-1].date()}  n={len(cum)}  '
      f'cum=${cum.iloc[-1]:.1f}M  peak=${cum.max():.1f}M')
