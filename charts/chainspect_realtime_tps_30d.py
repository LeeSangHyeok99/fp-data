"""
Real-time TPS (30D) by blockchain network (bar).
소스: Chainspect /chart?range-cm=month SvelteKit __data.json (tps.value, 30일 평균 실시간 TPS).
캐시: outputs/data/chainspect_realtime_tps_30d.csv. 투명 배경, 인포그래픽 슬롯 비율.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, gradient_rounded_bar, DPI  # noqa: E402

setup_font()
BLUE = '#4C8DFF'   # Chainspect 바 색 (레퍼런스)

df = pd.read_csv('outputs/data/chainspect_realtime_tps_30d.csv')

fig, ax = plt.subplots(figsize=(10.67, 4.7), dpi=DPI)
for i, v in enumerate(df['tps_30d']):
    gradient_rounded_bar(ax, x_center=i, width=0.62, height=v, color=BLUE, floor=0.45, round_top=False)

ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df['network'])
ax.set_yticks([0, 500, 1000, 1500, 2000])
ax.set_yticklabels(['0', '500', '1,000', '1,500', '2,000'])
ax.set_ylim(0, 2000)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

png, svg = save_chart(fig, 'chainspect_realtime_tps_30d', 'outputs/charts/blockchains/tps')
plt.close(fig); print(png)
