"""Upbit 전체 KRW 마켓 일 거래대금(7일 평균)을 BTC 사이클 top 4개 기준으로 정렬.

2x2 합본 1장 + 패널별 낱장 4장을 같이 뽑는다 (낱장이 수정하기 편해서).
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import COLORS, save_chart, setup_font  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

MINT = "#7fe3c3"
XLIM = (-78, 78)
OUTDIR = "outputs/charts/korea/volume"

PANELS = [
    # (window key, 패널 제목, 주석 기준일(None이면 최댓값), 주석 앞머리, 라벨 방향, 파일 접미사)
    ("2017-12", "Dec 2017 Top", None, "Peak", "left", "2017_12"),
    ("2021-04", "Apr 2021 Top", None, "Peak", "left", "2021_04"),
    ("2021-11", "Nov 2021 Top", None, "Peak", "right", "2021_11"),
    ("2025-10", "Oct 2025 Top", 10, "10/10 Spike", "right", "2025_10"),  # 2025-10-10 급등일
]

df = pd.read_csv("outputs/data/upbit_cycle_top_volume.csv")
setup_font()


def y_ticks(vmax):
    """0부터 시작하는 깔끔한 틱 4개 이하 (1/2/5 x 10^k 간격). ylim 안쪽만 찍는다."""
    for step in (1, 2, 5, 10, 20, 50):
        if vmax / step <= 3.2:
            top = vmax * 1.18
            return np.arange(0, top, step), top


def draw(ax, key, title, mark_day, prefix, side, fontscale=1.0):
    d = df[df["window"] == key].sort_values("day")
    d = d[(d["day"] >= XLIM[0]) & (d["day"] <= XLIM[1])]
    x, y = d["day"].values, d["usd_b"].values

    ax.set_facecolor("none")
    ax.plot(x, y, color=MINT, lw=1.6, solid_joinstyle="round")

    day = int(x[np.argmax(y)]) if mark_day is None else int(mark_day)
    val = float(y[list(x).index(day)])
    ax.scatter(day, val, s=45, color=MINT, zorder=5, linewidths=0)
    note = "%s %+dd, $%.1fB/d" % (prefix, day, val) if mark_day is None else \
           "%s, $%.1fB/d" % (prefix, val)
    ax.annotate(note, (day, val), textcoords="offset points",
                xytext=(10 if side == "right" else -10, 13),
                ha="left" if side == "right" else "right",
                fontsize=11 * fontscale, fontweight="bold", color=COLORS["text"])

    ticks, top = y_ticks(y.max())
    ax.set_ylim(-top * 0.02, top * 1.18)
    ax.set_yticks(ticks)
    ax.set_yticklabels(["$%.0fB" % t for t in ticks])
    ax.set_xlim(*XLIM)
    ax.set_xticks([-60, -30, 0, 30, 60])
    ax.set_xticklabels(["-60", "-30", "Top", "+30", "+60"])

    # top 기준선과 x축 baseline만 남긴다 (레퍼런스 레이아웃)
    ax.axvline(0, color=COLORS["text_secondary"], alpha=0.55, lw=1.0, zorder=1)
    ax.axhline(0, color=COLORS["text_secondary"], alpha=0.55, lw=1.0, zorder=1)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for axis in ("x", "y"):
        ax.tick_params(axis=axis, labelsize=12 * fontscale, length=0, pad=8,
                       colors=COLORS["text_secondary"])
    ax.set_title(title, fontsize=14 * fontscale, fontweight="bold",
                 color=COLORS["text"], pad=14)


# ── 2x2 합본 ──
fig, axes = plt.subplots(2, 2, figsize=(13, 7.2), dpi=150)
fig.patch.set_alpha(0)
for ax, cfg in zip(axes.ravel(), PANELS):
    draw(ax, *cfg[:5])
fig.tight_layout(h_pad=2.4, w_pad=3.0)
print(save_chart(fig, "upbit_cycle_top_volume_panels", OUTDIR)[0])
plt.close(fig)

# ── 패널별 낱장 ──
for key, title, mark_day, prefix, side, suffix in PANELS:
    fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=150)
    fig.patch.set_alpha(0)
    draw(ax, key, title, mark_day, prefix, side, fontscale=1.15)
    fig.tight_layout()
    print(save_chart(fig, "upbit_cycle_top_volume_%s" % suffix, OUTDIR)[0])
    plt.close(fig)
