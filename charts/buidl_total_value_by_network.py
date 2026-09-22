"""
BlackRock BUIDL total value by network, daily stacked area.
소스: rwa.xyz trpc tokenTimeseries (asset_id 2331, bridged_token_value_dollar, groupBy network).
캐시: outputs/data/buidl_total_value_by_network_daily.csv.
상위 5개 네트워크 + Others(Polygon, Optimism, Arbitrum, Tempo 합산). 투명 배경.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb
from matplotlib.patches import Polygon

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, DPI  # noqa: E402

setup_font()

# 스택 아래 -> 위. 색은 rwa.xyz 네트워크 색(레퍼런스)
ORDER = [('Others', '#777B80'), ('Aptos', '#D5FAD3'), ('BNB Chain', '#F1BA20'),
         ('Avalanche C-Chain', '#E84142'), ('Ethereum', '#32A6FF'), ('Solana', '#EF3EEC')]

df = pd.read_csv('outputs/data/buidl_total_value_by_network_daily.csv',
                 parse_dates=['date']).set_index('date') / 1e9
top5 = [n for n, _ in ORDER if n != 'Others']
df['Others'] = df.drop(columns=top5).sum(axis=1)

fig, ax = plt.subplots(figsize=(10.67, 4.45), dpi=DPI)
x = mdates.date2num(df.index)
bottom = np.zeros(len(df))
for name, color in ORDER:
    top = bottom + df[name].values
    # 레이어별 세로 그라데이션: 위쪽 원색 -> 아래쪽 어둡게
    f = np.linspace(1.0, 0.62, 256)[:, None]
    rgba = np.ones((256, 1, 4)); rgba[..., :3] = (np.array(to_rgb(color)) * f)[:, None, :]; rgba[..., 3] = 0.95
    im = ax.imshow(rgba, aspect='auto', extent=[x[0], x[-1], bottom.min(), top.max()],
                   origin='upper', interpolation='bilinear', zorder=3)
    poly = Polygon(np.column_stack([np.r_[x, x[::-1]], np.r_[top, bottom[::-1]]]),
                   transform=ax.transData, facecolor='none', edgecolor='none')
    ax.add_patch(poly); im.set_clip_path(poly)
    ax.plot(df.index, top, color=color, linewidth=0.8, zorder=4)
    bottom = top

ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(['$0B', '$1B', '$2B', '$3B'])
ax.set_ylim(0, 3.2)
ax.set_xlim(df.index.min(), df.index.max())
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'stacked')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

png, svg = save_chart(fig, 'buidl_total_value_by_network', 'outputs/charts/blackrock/buidl')
plt.close(fig)
print(png, df.index.max().date(), df.iloc[-1][[n for n, _ in ORDER]].round(3).to_dict())
