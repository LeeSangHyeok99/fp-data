"""
Cap: Reserves vs Underwriting Collateral composition (100% stacked horizontal bar)
Four Pillars 스타일. 두 시점(First article Dec 2025 / Current Jun 2026) 비교.
Source: DeFiLlama, Cap Q1 2026 Update (protocol disclosures)
수치는 사용자 제공 보정값: Dec 2025 R=317M/C=54M, Jun 2026 R=73M/C=204M
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import create_figure, save_chart, setup_font

setup_font()

# -----------------------------------------------------------------------------
# 데이터 (사용자 제공 보정값)
# -----------------------------------------------------------------------------
rows = [
    {"label": "First article\n(Dec 2025)", "reserve": 317, "collateral": 54},
    {"label": "Current\n(Jun 2026)",       "reserve": 73,  "collateral": 204},
]

RESERVE = "#6b7d9e"     # 슬레이트 블루 (idle capital)
COLLATERAL = "#3a8079"  # 틸 (active risk capital)
TEXT = "#ffffff"
LABEL = "#d1d4dc"

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

y_pos = [1, 0]  # 위: Dec 2025, 아래: Jun 2026
bar_h = 0.5

for y, row in zip(y_pos, rows):
    total = row["reserve"] + row["collateral"]
    r_pct = row["reserve"] / total * 100
    c_pct = row["collateral"] / total * 100

    # Reserves 세그먼트
    ax.barh(y, r_pct, height=bar_h, color=RESERVE, zorder=3)
    # Collateral 세그먼트
    ax.barh(y, c_pct, left=r_pct, height=bar_h, color=COLLATERAL, zorder=3)

    # 세그먼트 라벨 (좁은 세그먼트는 작은 폰트)
    r_fs = 13 if r_pct >= 18 else 10
    c_fs = 13 if c_pct >= 18 else 10
    ax.text(r_pct / 2, y, f"Reserves {r_pct:.0f}%\n~${row['reserve']}M",
            ha="center", va="center", fontsize=r_fs, fontweight="bold", color=TEXT, zorder=4)
    ax.text(r_pct + c_pct / 2, y, f"Collateral {c_pct:.0f}%\n~${row['collateral']}M",
            ha="center", va="center", fontsize=c_fs, fontweight="bold", color=TEXT, zorder=4)

    # 행 라벨 (왼쪽)
    ax.text(-2, y, row["label"], ha="right", va="center",
            fontsize=14, fontweight="bold", color=LABEL, zorder=4)

# -----------------------------------------------------------------------------
# 축 정리
# -----------------------------------------------------------------------------
ax.set_xlim(0, 100)
ax.set_ylim(-0.6, 1.6)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# 행 라벨 공간 확보 + 우측 여백
ax.set_xlim(-26, 102)

fig.tight_layout()
png, svg = save_chart(fig, "cap_reserve_collateral_composition", "outputs/charts/cap/reserves")
print("saved:", png, svg)
