import sys
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/asxn_hl_buybacks_weekly.csv', parse_dates=['week_end'])

HIST = '#44544f'   # 히스토리: 무채 슬레이트 틸
MINT = '#6ff2d0'   # 2Q26 하이라이트: 밝은 민트

# 2Q26 = 주 종료일이 2026-04-05 ~ 2026-06-28 (분기 합 = $140.7M)
q2 = (df['week_end'] >= '2026-04-05') & (df['week_end'] <= '2026-06-28')
colors = [MINT if f else HIST for f in q2]

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.bar(df['week_end'], df['buyback_musd'], width=5.0, color=colors, zorder=3)

# 2Q26 라벨
ax.text(pd.Timestamp('2026-05-20'), 34, '2Q26', color=MINT,
        fontsize=20, fontweight='bold', ha='center', va='bottom')

ax.set_ylim(0, 42)
ax.set_yticks([0, 10, 20, 30, 40])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

month_ticks = pd.to_datetime(
    ['2025-04-01', '2025-07-01', '2025-10-01', '2026-01-01', '2026-04-01', '2026-07-01'])
ax.set_xticks(month_ticks)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['week_end'].min() - pd.Timedelta(days=6),
            df['week_end'].max() + pd.Timedelta(days=6))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0, pad=12, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

out = 'outputs/charts/hyperliquid/revenue'
Path(out).mkdir(parents=True, exist_ok=True)
fig.savefig(f'{out}/asxn_af_weekly_buyback.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{out}/asxn_af_weekly_buyback.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f'{out}/asxn_af_weekly_buyback.png')
