"""
Securitize Platform by Asset Class (Total RWA Value) — four-pillars donut.
Reference: rwa.xyz Exhibit 15A, as of 07/10/2026.
Values read directly from reference legend (Securitize platform scale ~$4.1B,
cross-checked vs Securitize token file total $4.4B).
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import donut_leader_labels, save_chart

df = pd.read_csv("outputs/data/securitize_asset_class.csv")

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
    start_angle=90,
    xlim=(-2.7, 2.2),
    ylim=(-1.6, 2.15),
    gradient=True,
)

# ~550px wide output: render at tuned proportions, pick DPI to hit target width.
import os
out_dir = "outputs/charts/rwa/securitize"
os.makedirs(out_dir, exist_ok=True)
TARGET_W = 540
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_W / bb.width
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/securitize_asset_class_donut.{ext}", dpi=dpi,
                facecolor="none", edgecolor="none", bbox_inches="tight",
                transparent=True)
print("saved at dpi", round(dpi, 1))
