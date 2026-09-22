"""
Solana: Stablecoin Total Supply, quarterly Q2 2025 ~ Q2 2026 (bar).
소스: Blockworks Research (레퍼런스 이미지 디지타이즈, Q2 2026 = $16.3B 기준).
four-pillars 투명 배경, 인포그래픽 슬롯 비율.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, gradient_rounded_bar, DPI  # noqa: E402

setup_font()
SOLANA = '#9945FF'

df = pd.read_csv('outputs/data/solana_stablecoin_supply_quarterly.csv')

fig, ax = plt.subplots(figsize=(10.67, 4.3), dpi=DPI)
for i, v in enumerate(df['supply_busd']):
    gradient_rounded_bar(ax, x_center=i, width=0.62, height=v, color=SOLANA,
                         floor=0.45, round_top=False)

ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df['quarter'])
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels(['$0B', '$5B', '$10B', '$15B', '$20B'])
ax.set_ylim(0, 20)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

png, svg = save_chart(fig, 'solana_stablecoin_supply_quarterly', 'outputs/charts/solana/stablecoin')
plt.close(fig)
print(png)
