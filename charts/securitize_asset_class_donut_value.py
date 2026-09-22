"""
Securitize Platform by Asset Class — four-pillars donut, DOLLAR-VALUE labels.
Value-labeled variant of securitize_asset_class_donut.py (which uses %).
Reference: rwa.xyz Exhibit 15A, as of 07/10/2026.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import donut_leader_labels

df = pd.read_csv("outputs/data/securitize_asset_class.csv")


def fmt(v):  # $M values -> $2.3B / $357.5M, matching reference
    return f"${v/1000:.1f}B" if v >= 1000 else f"${v:.1f}M"


SUBLABELS = {row.token: fmt(row.value) for row in df.itertuples()}

LABEL_POS = {
    "US Treasury Debt": (+1.72, -0.30, "right"),
    "Others":           (+0.28, +1.88, "top"),
    "Private Equity":   (-0.95, +1.66, "left"),
    "Active Strategies":(-1.58, +1.12, "left"),
    "Stocks":           (-1.80, +0.62, "left"),
    "Corporate Credit": (-1.88, +0.10, "left"),
    "Venture Capital":  (-1.62, -0.62, "left"),
}

fig, ax = donut_leader_labels(
    values=df["value"].tolist(),
    labels=df["token"].tolist(),
    colors=df["color"].tolist(),
    label_pos=LABEL_POS,
    sublabels=SUBLABELS,
    start_angle=90,
    xlim=(-2.7, 2.2),
    ylim=(-1.6, 2.15),
    gradient=True,
)

import os
out_dir = "outputs/charts/rwa/securitize"
os.makedirs(out_dir, exist_ok=True)
TARGET_W = 540
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_W / bb.width
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/securitize_asset_class_donut_value.{ext}", dpi=dpi,
                facecolor="none", edgecolor="none", bbox_inches="tight",
                transparent=True)
print("saved at dpi", round(dpi, 1))
