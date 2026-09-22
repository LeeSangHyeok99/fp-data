"""
Total Curated Vault TVL (DefiLlama Risk Curators)
Four Pillars 스타일 area/line 차트 (DefiLlama 실데이터 재현)
Source: https://defillama.com/protocols/risk-curators
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, area_glow, create_figure, endpoint_dot, save_chart

df = pd.read_csv("outputs/data/defillama_curated_vault_tvl.csv", parse_dates=["date"])
df = df[df["date"] >= "2023-06-01"].reset_index(drop=True)
df["tvl_b"] = df["tvl"] / 1e9

LINE = "#2d7ff9"  # DefiLlama TVL 시리즈 블루

fig, ax = create_figure("area")

area_glow(ax, df["date"], df["tvl_b"], color=LINE, max_alpha=0.20)
ax.plot(df["date"], df["tvl_b"], color=LINE, linewidth=2.0, zorder=4)
endpoint_dot(ax, df["date"].iloc[-1], df["tvl_b"].iloc[-1], color=LINE, size=42)

ticks = [0, 2.5, 5, 7.5, 10]
ax.set_ylim(0, 11)
ax.set_yticks(ticks)
ax.set_yticklabels([f"${v:g}B" if v == int(v) else f"${v:.1f}B" for v in ticks])

ax.set_xlim(df["date"].min(), df["date"].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "area")
ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=16)

png, svg = save_chart(fig, "defillama_curated_vault_tvl", "outputs/charts/defi/tvl")
print("saved:", png, svg)
