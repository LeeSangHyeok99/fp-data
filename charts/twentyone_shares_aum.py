"""
21Shares Total AUM by product (Four Pillars 표준 도넛 + 외부 리더라벨)
config.donut_leader_labels() 사용. 비율은 이미지 슬라이스에서 추정(실데이터 미공개).
Source: 21Shares AUM dashboard (Total $1,008,836,372.03), 이미지 추출

수정법: LABEL_POS (dot_x, dot_y, mode) / ELBOW [(x,y),...]
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import auto_label_pos, donut_leader_labels, save_chart

# =============================================================================
# ▼▼▼ 선/라벨 위치 (None 이면 auto_label_pos 자동) ▼▼▼
# =============================================================================
LABEL_POS = {
    "ABNB":    (+1.46, -0.30, "right"),
    "ABTC":    (+1.20, -1.18, "right"),
    "HODL":    (-1.30, -1.10, "left"),
    "AETH":    (-1.52, -0.40, "left"),
    "AXTZ":    (-1.56, +0.30, "left"),
    "MOON":    (-1.40, +0.86, "left"),
    "ABBA":    (-1.02, +1.26, "top"),
    "ADOT":    (-0.58, +1.46, "top"),
    "AXRP":    (-0.16, +1.56, "top"),
    "KEYS":    (+0.28, +1.50, "top"),
    "ABCH":    (+0.70, +1.34, "top"),
    "SBTC":    (+1.06, +1.10, "top"),
}
ELBOW = {}
START_ANGLE = 90
# =============================================================================

df = pd.read_csv("outputs/data/twentyone_shares_aum.csv")

fig, ax = donut_leader_labels(
    values=df["pct"].tolist(),
    labels=df["token"].tolist(),
    colors=df["color"].tolist(),
    label_pos=LABEL_POS,
    elbow=ELBOW,
    start_angle=START_ANGLE,
    xlim=(-2.1, 2.1),
    ylim=(-1.7, 1.9),
)

png, svg = save_chart(fig, "twentyone_shares_aum", "outputs/charts/21shares/aum")
print("saved:", png, svg)
