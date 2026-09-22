"""
Vault TVL Market Share (Morpho / Veda / Concrete / Kamino / Upshift / Euler / Midas / Fusion)
four-pillars 표준 도넛. 소스: DefiLlama, Morpho, Kamino.

리더선 규약: 웨지 중앙 각도에서 호에 수직(= 반지름 방향)으로 뻗다가 한 번만 꺾여
라벨까지 수평(ㅡ)으로 간다. 꺾이는 높이(Y_ELBOW)와 도트 x(X_DOT)만 지정하면
뻗는 길이는 각도에서 역산한다.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import donut_leader_labels, save_chart  # noqa: E402

CSV_PATH = 'outputs/data/vault_tvl_market_share.csv'
OUT_NAME = 'vault_tvl_market_share'
OUT_DIR  = 'outputs/charts/defi/vault'
START_ANGLE = 90

df = pd.read_csv(CSV_PATH).sort_values('tvl', ascending=False)

# 왼쪽으로 나가는 라벨은 12시에 가까운 웨지일수록 높은 곳에서 꺾어야 다른
# 리더선 위를 지나간다. 도트는 웨지 가까이 붙여 수평 구간을 짧게 유지한다.
Y_ELBOW = {'Euler': 1.70, 'Upshift': 1.40, 'Kamino': 1.10, 'Concrete': 0.88,
           'Fusion': 1.30}
X_DOT   = {'Euler': -0.46, 'Upshift': -1.34, 'Kamino': -0.78, 'Concrete': -1.36,
           'Fusion': 0.30}

# Veda와 Morpho는 꺾지 않는다. 도트 높이에서 호에 바로 붙여 다른 선의 수평 구간과
# 나란한 직선 하나로 만든다(웨지가 넓어 그 높이가 해당 구간 안에 있다).
# Morpho는 차트 한가운데 높이(y=0)에서 붙인다.
LEVEL = {'Veda': 0.42, 'Morpho': 0.0}
X_LEVEL = {'Veda': -1.20, 'Morpho': 1.30}

# Midas는 꺾지 않고 위로만 간다. 도트 x를 웨지 중앙 각도의 x에 맞추면 수직선.
Y_TOP = {'Midas': 1.62}

frac = df['tvl'] / df['tvl'].sum()
mid = dict(zip(df['protocol'],
               np.deg2rad(START_ANGLE - 360 * (frac.cumsum() - frac / 2))))

ANGLE_RUN = {lab: y / np.sin(mid[lab]) - 1 for lab, y in Y_ELBOW.items()}

LABEL_POS = {}
for lab in df['protocol']:
    if lab in LEVEL:
        LABEL_POS[lab] = (X_LEVEL[lab], LEVEL[lab],
                          'left' if X_LEVEL[lab] < 0 else 'right')
    elif lab in Y_TOP:
        LABEL_POS[lab] = (float(np.cos(mid[lab])), Y_TOP[lab], 'top')
    else:
        LABEL_POS[lab] = (X_DOT[lab], None,
                          'left' if X_DOT[lab] < 0 else 'right')

fig, ax = donut_leader_labels(
    values=df['tvl'].tolist(),
    labels=df['protocol'].tolist(),
    colors=df['color'].tolist(),
    label_pos=LABEL_POS,
    start_angle=START_ANGLE,
    xlim=(-2.2, 2.05),
    ylim=(-1.12, 2.0),
    gradient=True,
    angled=True,
    angle_run=ANGLE_RUN,
    level=set(LEVEL),
)
print(*save_chart(fig, OUT_NAME, OUT_DIR))
