"""
Prediction Market Trading Volume by Sector (last 12M) — four-pillars donut.
Data: The Block per-category daily USD volume JSONs (Kalshi / Polymarket),
2025-09-01 ~ 2026-08-31 합계. 두 플랫폼의 카테고리 체계가 달라 공통 섹터로 묶음.
합산 버전 1장 + 플랫폼별 2장을 같은 섹터 색으로 그린다.
"""

import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import donut_leader_labels

df = pd.read_csv('outputs/data/prediction_market_volume_by_sector.csv')
OUT = 'outputs/charts/prediction-markets/volume'
os.makedirs(OUT, exist_ok=True)

# 파일명: (값 컬럼, 하단 캡션, 라벨 위치, 꺾인 리더선을 쓸 라벨)
VARIANTS = {
    'prediction_market_volume_by_sector': ('total_usd', None, True, {
        'Sports':               (+1.32, -0.45, 'right'),
        'Crypto':               (-1.38, -0.30, 'left'),
        'Other':                (-1.42, +0.55, 'left'),
        'Politics & Elections': (-1.08, +1.18, 'left'),
        'Culture & Media':      (-0.05, +1.48, 'top'),
        'Economy & Finance':    (+0.88, +1.34, 'right'),
    }),
    'kalshi_volume_by_sector': ('kalshi_usd', 'Kalshi',
                                {'Other', 'Politics & Elections',
                                 'Culture & Media', 'Economy & Finance'}, {
        'Sports':               (+1.32, 0.0, 'right'),
        'Crypto':               (-1.38, None, 'left'),
        'Other':                (-1.36, None, 'left'),
        'Politics & Elections': (-0.55, None, 'left'),
        'Culture & Media':      (+0.28, None, 'right'),
        'Economy & Finance':    (+0.62, None, 'right'),
    }),
    'polymarket_volume_by_sector': ('polymarket_usd', 'Polymarket',
                                    {'Crypto', 'Other', 'Culture & Media',
                                     'Economy & Finance'}, {
        'Sports':               (+1.36, None, 'right'),
        'Crypto':               (-1.18, None, 'left'),
        'Politics & Elections': (-1.42, None, 'left'),
        'Other':                (-1.14, None, 'left'),
        'Culture & Media':      (-0.62, None, 'left'),
        'Economy & Finance':    (+0.20, None, 'right'),
    }),
}

# 라벨별로 리더선을 더 길게 뽑아야 하는 경우(겹침 회피)
RUNS = {
    'polymarket_volume_by_sector': {'Culture & Media': 0.62,
                                    'Economy & Finance': 0.30},
    # 12시 근처에 몰린 작은 웨지 3개는 뻗는 길이를 달리해 선/라벨이 안 겹치게 한다
    'kalshi_volume_by_sector': {'Politics & Elections': 0.62,
                                'Culture & Media': 0.62,
                                'Economy & Finance': 0.28},
}

# 넓은 웨지는 도트 높이에서 호에 바로 붙이면 수평 = 호에 수직
LEVEL = {'kalshi_volume_by_sector': {'Sports'}}

for name, (col, caption, angled, label_pos) in VARIANTS.items():
    d = df.sort_values(col, ascending=False)
    fig, ax = donut_leader_labels(
        values=d[col].tolist(),
        labels=d['sector'].tolist(),
        colors=d['color'].tolist(),
        label_pos=label_pos,
        start_angle=90,
        xlim=(-2.4, 2.3),
        ylim=(-1.72, 1.8),
        gradient=True,
        angled=angled,
        angle_run=RUNS.get(name, 0.34),
        level=LEVEL.get(name, ()),
    )
    if caption:
        ax.text(0, -1.34, caption, ha='center', va='top', fontsize=19,
                fontweight='bold', color='#C7CCD3')

    TARGET_W = 720
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    dpi = TARGET_W / bb.width
    for ext in ('png', 'svg'):
        fig.savefig(f'{OUT}/{name}.{ext}', dpi=dpi, facecolor='none',
                    edgecolor='none', bbox_inches='tight', transparent=True)
    print(f'{OUT}/{name}.png  (총 ${d[col].sum() / 1e9:.1f}B)')
