"""
USDC share of all-time x402 volume (Artemis reference) — four-pillars donut.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import donut_leader_labels, save_chart

df = pd.read_csv("outputs/data/x402/x402_usdc_share.csv")

# Other 웨지(0.09%)의 중앙각은 90.16도. 그 x로 수직으로 올린 뒤 직각으로 꺾어 뺀다
LABEL_POS = {
    "USDC":  (+1.06, -0.72, "right"),
    "Other": (+0.72, +1.17, "right"),
}
ELBOW = {"Other": [(-0.0028, +1.17)]}

fig, ax = donut_leader_labels(
    values=df["share_pct"].tolist(),
    labels=df["token"].tolist(),
    colors=df["color"].tolist(),
    label_pos=LABEL_POS,
    elbow=ELBOW,
    start_angle=90,
    xlim=(-1.7, 2.0),
    ylim=(-1.35, 1.75),
    name_fs=21, pct_fs=19, top_name_fs=21, top_pct_fs=19,
    label_gap=0.20, top_gap=0.20,
    gradient=True,
    level=("USDC",),   # 웨지가 거의 한 바퀴라 중앙각 대신 도트 높이에서 호에 붙인다
)

save_chart(fig, "x402_usdc_share_donut", output_dir="outputs/charts/x402/volume")
print("saved")
