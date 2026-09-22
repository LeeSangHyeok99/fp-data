"""
State Street Galaxy OnChain Liquidity Sweep Fund (SWEEP) total value, daily.
소스: rwa.xyz trpc tokenTimeseries (bridged_token_value_dollar, Solana).
캐시: outputs/data/sweep_total_value_daily.csv (rwaxyz_sweep_total_value_trpc.json 디코드).
four-pillars 투명 배경, 인포그래픽 1600x540 슬롯 비율.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, DPI  # noqa: E402
setup_font()

COLOR = '#EF3EEC'  # rwa.xyz Solana 네트워크 색 (레퍼런스)

df = pd.read_csv('outputs/data/sweep_total_value_daily.csv', parse_dates=['date'])
y = df['total_value_usd'] / 1e6
x = mdates.date2num(df['date'])

fig, ax = plt.subplots(figsize=(10.67, 4.6), dpi=DPI)
ax.plot(df['date'], y, color=COLOR, linewidth=2.2, zorder=4)

# 세로 그라데이션 필: 라인 근처 진하고 아래로 갈수록 투명
grad = np.linspace(0.45, 0.0, 256)[:, None] ** 1.4
rgba = np.zeros((256, 1, 4)); rgba[..., :3] = matplotlib.colors.to_rgb(COLOR); rgba[..., 3] = grad
im = ax.imshow(rgba, aspect='auto', extent=[x.min(), x.max(), 0, y.max()],
               origin='upper', interpolation='bilinear', zorder=2)
poly = Polygon(np.column_stack([np.r_[x, x[-1], x[0]], np.r_[y, 0, 0]]),
               transform=ax.transData, facecolor='none', edgecolor='none')
ax.add_patch(poly); im.set_clip_path(poly)

ax.set_yticks([0, 100, 200, 300])
ax.set_yticklabels(['$0M', '$100M', '$200M', '$300M'])
ax.set_ylim(0, 300)
ax.set_xlim(df['date'].min(), df['date'].max())
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'area')
ax.tick_params(axis='both', labelsize=14)   # X/Y 동일 크기
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

png, svg = save_chart(fig, 'sweep_total_value', 'outputs/charts/state_street/sweep')
plt.close(fig)
print(png, svg, df['date'].max().date(), round(y.iloc[-1], 1))
