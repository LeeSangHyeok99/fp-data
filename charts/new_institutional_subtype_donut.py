"""
New Institutional Investors by Subtype, 연도별 컴팩트 도넛 12장 - four-pillars 내재화
데이터: 사용자 제공. New = 해당 연도에 처음 등장한 기관 투자자. 2026은 YTD.
덱에서 한 줄로 늘어놓는 용도라 프레임을 정사각형으로 최소화하고, 리더라인과
시리즈명을 빼고 링 + 퍼센트만 남긴다. 색은 스택 바의 기관 서브타입 색과 동일.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, DPI  # noqa: E402

SUBTYPES = [
    ('generalist',        '#4a7fd4'),  # Generalist VC / Growth / PE
    ('tradfi_am_mi',      '#6d6ce0'),  # TradFi / Asset Manager / Market Infra
    ('corporate',         '#9a72d8'),  # Corporate / CVC
    ('sovereign',         '#c47ec8'),  # Sovereign / Government-backed
    ('tradfi_crypto_arm', '#e08fa8'),  # TradFi Crypto Arm
]
COLOR = dict(SUBTYPES)
ORDER = [k for k, _ in SUBTYPES]

SEP = '#141414'      # 웨지 구분선 (다크 배경색)
# 라벨은 링 바깥 LABEL_R 지점에서 '바깥쪽으로' 자란다(중앙정렬 아님).
# 중앙정렬로 두면 글자 절반이 링 위로 올라와 붙어 보인다.
RING_R = 1.0         # 링 반지름
LABEL_R = 1.14       # 라벨이 시작하는 반지름 (링과 약 18px 간격)
MIN_PCT = 2.5        # 이보다 작은 조각은 라벨 생략 (겹침 방지)

df = pd.read_csv('outputs/data/new_institutional_subtype_share.csv')

OUTPUT_DIR = Path('outputs/charts/crypto_funding/vc')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

setup_font()
grad = np.repeat(np.linspace(0, 1, 256).reshape(-1, 1), 2, axis=1)

for year, g in df.groupby('year'):
    g = g.set_index('subtype').reindex([s for s in ORDER if s in g['subtype'].values])
    values = g['count'].tolist()
    colors = [COLOR[s] for s in g.index]

    # 주신 share와 count 기반 계산치가 어긋나지 않는지 확인 (반올림 오차 허용)
    pct = np.array(values) / sum(values) * 100
    assert np.allclose(pct, g['share'].values, atol=0.02), \
        f'{year} share mismatch: {pct.round(2).tolist()} vs {g["share"].tolist()}'

    fig, ax = plt.subplots(figsize=(3.0, 3.2), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    wedges, _ = ax.pie(
        values, colors=colors, startangle=90, counterclock=False, radius=RING_R,
        wedgeprops=dict(width=0.40, edgecolor=SEP, linewidth=2.0,
                        antialiased=True),
    )

    # 웨지별 세로 그라데이션 (상단 밝음 → 하단 어두움)
    for w, c in zip(wedges, colors):
        base = np.array(mcolors.to_rgb(c))
        cmap = mcolors.LinearSegmentedColormap.from_list(
            'g', [base * 0.82, base + (1 - base) * 0.32])
        im = ax.imshow(grad, extent=[-RING_R, RING_R, -RING_R, RING_R],
                       origin='lower', cmap=cmap,
                       aspect='auto', interpolation='bilinear', zorder=1)
        im.set_clip_path(w)
        w.set_facecolor('none')
        w.set_zorder(1.5)

    # 퍼센트만 링 바깥에 표기 (이름/리더라인 없음, 색으로 시리즈 구분)
    for w, c, p in zip(wedges, colors, pct):
        if p < MIN_PCT:
            continue
        a = np.deg2rad((w.theta1 + w.theta2) / 2)
        cx, cy = np.cos(a), np.sin(a)
        ha = 'left' if cx > 0.2 else 'right' if cx < -0.2 else 'center'
        va = 'bottom' if cy > 0.2 else 'top' if cy < -0.2 else 'center'
        ax.text(cx * LABEL_R, cy * LABEL_R, f'{p:.1f}%', ha=ha, va=va,
                fontsize=12, fontweight='bold', color=c, zorder=4)

    # 연도 (링 위, 흰색). 퍼센트 라벨 최대 반지름 1.26보다 충분히 위에 둔다.
    n = sum(values)
    year_label = (f'{year} YTD (n = {n})' if year == 2026
                  else f'{year} (n = {n})')
    ax.text(0, 1.60, year_label, ha='center', va='bottom',
            fontsize=15, fontweight='bold', color='#ffffff', zorder=4)

    # 프레임 고정: bbox_inches='tight' 대신 figsize 그대로 저장한다.
    # xlim/ylim 비율을 figsize 비율(3.0:3.2)에 맞춰 aspect='equal'이 축을
    # 줄이지 않게 한다.
    ax.set_position([0, 0, 1, 1])
    # 라벨이 가장 길게 뻗는 연도(2017, 2023)도 프레임에 여유 있게 들어가도록
    # 데이터 범위를 넓혀 잡는다. 세로는 상단 연도 라벨만큼 중심을 위로 올린다.
    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.66, 2.50)
    ax.set_aspect('equal')
    ax.axis('off')

    name = f'new_institutional_subtype_{year}'
    for fmt in ('png', 'svg'):
        fig.savefig(OUTPUT_DIR / f'{name}.{fmt}', dpi=DPI, facecolor='none',
                    edgecolor='none', transparent=True, format=fmt)
    plt.close(fig)
    dropped = [f'{p:.2f}%' for p in pct if p < MIN_PCT]
    print(f'{year}: n={sum(values)}, slices={len(values)}'
          + (f', label omitted {dropped}' if dropped else ''))
