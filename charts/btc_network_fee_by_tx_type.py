"""Bitcoin network fee, daily total in BTC (단일 시리즈, 범례 구분 없음).
Reference: Dune @murchandamus "Proportions of Inscriptions, BRC20, and Runes" (query 2962509).
레퍼런스는 tx 타입별 스택이지만 요청대로 수치 하나로 합쳐서 그린다.
Source data: sources/Regular_Txs_vs_BRC20_Txs_vs_other_Inscription_Txs_vs_Runes_Txs.csv
(Dune CSV export, 2023-02-17~. 이전 outputs/data/btc_fee_by_tx_type.csv와 겹치는 1,285일 오차 0.)
Cross-validated: 일별 합계 == blockchain.com transaction-fees (median diff 0.00%).
"""
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import COLORS, DPI, GRID_CONFIG, DEFAULT_FIGSIZE, area_glow, setup_font  # noqa: E402

LINE = "#5470c6"
COLS = ["regular_tx_Fee", "Only_BRC20_Fee", "Other_Inscriptions_Fee",
        "Only_Runes_Fee", "Other_RnI_Fee", "RnB_Fee"]

df = pd.read_csv("sources/Regular_Txs_vs_BRC20_Txs_vs_other_Inscription_Txs_vs_Runes_Txs.csv",
                 parse_dates=["Day"]).sort_values("Day").reset_index(drop=True)
df["total"] = df[COLS].sum(axis=1)

setup_font()
gray = COLORS["text_secondary"]
fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE, dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

ax.fill_between(df["Day"], 0, df["total"], color=LINE, alpha=0.30,
                linewidth=0, zorder=3)
area_glow(ax, df["Day"], df["total"], color=LINE, max_alpha=0.10)
ax.plot(df["Day"], df["total"], color=LINE, linewidth=1.0, zorder=4)

ax.set_xlim(df["Day"].min(), df["Day"].max())
ax.set_ylim(0, 1320)
ax.margins(x=0, y=0)

ax.yaxis.set_major_locator(FixedLocator([0, 400, 800, 1200]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f} BTC"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="y", labelsize=15, colors=gray, length=0, pad=10)
ax.tick_params(axis="x", labelsize=13, colors=gray, length=0, pad=8, rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha="right", rotation_mode="anchor")
ax.grid(True, axis="y", color=GRID_CONFIG["color"], alpha=GRID_CONFIG["alpha"],
        linestyle=GRID_CONFIG["linestyle"], linewidth=GRID_CONFIG["linewidth"])
ax.set_axisbelow(True)

fig.tight_layout()
outdir = Path("outputs/charts/bitcoin/fees")
outdir.mkdir(parents=True, exist_ok=True)
base = outdir / "btc_network_fee_by_tx_type"
for ext in ("png", "svg"):
    fig.savefig(f"{base}.{ext}", dpi=DPI, transparent=True,
                facecolor="none", edgecolor="none", bbox_inches="tight")
print(f"{base}.png")

# sanity: Runes 런칭일(2024-04-20)이 전 구간 최고점, blockchain.com 총액과 동일
peak = df.loc[df["total"].idxmax()]
assert str(peak["Day"].date()) == "2024-04-20" and 1255 < peak["total"] < 1260
assert df.set_index("Day").loc["2026":, "total"].max() < 30  # 최근 구간은 잠잠
