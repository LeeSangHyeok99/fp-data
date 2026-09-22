"""
Cap: Organic deposits rate / Unstaked share vs peers (각각 별도 차트)
Four Pillars 스타일. 두 개의 단일 막대 차트를 따로 출력.
  1) Non-farming deposit share: Q1 start 59.3% → Q1 end 89.7%
  2) Unstaked share: Sky USDS 23% / Cap cUSD 30% / Ethena USDe 40%
Source: https://www.cap.app/blog/cap-investor-update-q1-2026
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, GRID_CONFIG, setup_font

setup_font()

TEXT = "#d1d4dc"
SECONDARY = COLORS["text_secondary"]

ORGANIC = [("Q1 start", 59.3, "#ccd5db"), ("Q1 end", 89.7, "#2f7e74")]
UNSTAKED = [("Sky\nUSDS", 23, "#6b7fa3"), ("Cap\ncUSD", 30, "#2f7e74"),
            ("Ethena\nUSDe", 40, "#c7c7d2")]


def style_ax(ax, yticks):
    ax.set_facecolor("none")
    ax.grid(True, axis="y", color=GRID_CONFIG["color"], alpha=GRID_CONFIG["alpha"],
            linestyle=GRID_CONFIG["linestyle"], linewidth=GRID_CONFIG["linewidth"])
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{v}%" for v in yticks])
    ax.tick_params(axis="y", labelsize=22, length=0, colors=SECONDARY)
    ax.tick_params(axis="x", labelsize=22, length=0, colors=SECONDARY, pad=10)


def draw_bars(ax, rows, ymax, fmt, width=0.58):
    xs = range(len(rows))
    for x, (lab, val, col) in zip(xs, rows):
        ax.bar(x, val, width=width, color=col, zorder=3)
        ax.text(x, val + ymax * 0.022, fmt(val), ha="center", va="bottom",
                fontsize=23, fontweight="bold", color=TEXT, zorder=4)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_xlim(-0.7, len(rows) - 0.3)
    ax.set_ylim(0, ymax)


def render(name, rows, yticks, fmt, width=0.58):
    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=150)
    fig.patch.set_alpha(0)
    draw_bars(ax, rows, yticks[-1], fmt, width)
    style_ax(ax, yticks)
    fig.tight_layout()
    out = Path("outputs/charts/cap/deposits")
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", facecolor="none", edgecolor="none",
                    bbox_inches="tight", transparent=True,
                    dpi=150 if ext == "png" else None)
    plt.close(fig)
    print("saved:", out / f"{name}.png")


render("cap_organic_deposit_share", ORGANIC, [0, 20, 40, 60, 80, 100], lambda v: f"{v:.1f}%")
render("cap_unstaked_share_vs_peers", UNSTAKED, [0, 10, 20, 30, 40, 50], lambda v: f"{v:.0f}%")
