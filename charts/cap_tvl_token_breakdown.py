"""
Cap TVL token breakdown (Four Pillars 표준 도넛 + 외부 리더라벨)
config.donut_leader_labels() 사용. 라벨 위치는 LABEL_POS 로 손으로 조정,
선이 도넛/다른 선과 겹치면 ELBOW 로 꺾어 우회한다.
Source: https://defillama.com/protocol/tvl/cap  (api.llama.fi/protocol/cap, tokensInUsd)

수정법:
  LABEL_POS: "TOKEN": (dot_x, dot_y, mode)   도트(선 끝)+글자 위치
    mode "left"(글자 우정렬,도트 좌) | "right"(글자 좌정렬,도트 우) | "top"(글자 도트 위)
  ELBOW: "TOKEN": [(x,y),...]   선이 거쳐가는 꺾임점(선택). 비우면 직선.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import donut_leader_labels, save_chart

# =============================================================================
# ▼▼▼ 선/라벨 위치 ▼▼▼
# =============================================================================
LABEL_POS = {
    "UNIBTC":  (+1.34, -0.55, "right"),
    "USDC":    (-1.40, -0.42, "left"),
    "WSTETH":  (-1.46, +0.06, "left"),
    "WEETH":   (-1.40, +0.52, "left"),
    "SOLVBTC": (-0.92, +1.30, "top"),
    "LBTC":    (-0.46, +1.52, "top"),
    "WTGXX":   (-0.02, +1.42, "top"),
    "SFRXUSD": (+0.40, +1.52, "top"),
    "Other":   (+0.82, +1.30, "top"),
}
ELBOW = {
    # "WEETH": [(-1.05, 0.52)],
}
START_ANGLE = 90
# =============================================================================

df = pd.read_csv("outputs/data/cap_tvl_token_breakdown.csv")

fig, ax = donut_leader_labels(
    values=df["pct"].tolist(),
    labels=df["token"].tolist(),
    colors=df["color"].tolist(),
    label_pos=LABEL_POS,
    elbow=ELBOW,
    start_angle=START_ANGLE,
)

png, svg = save_chart(fig, "cap_tvl_token_breakdown", "outputs/charts/cap/tvl")
print("saved:", png, svg)
