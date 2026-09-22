"""
DoubleZero vs. public internet: round-trip time reduction (%), top 22 metro pairs.
소스: sources/dz-vs-internet-latency.csv ("RTT Improvement (%)" 컬럼).

outputs/charts/Group 1991501171.svg(피그마 원본)의 레이아웃을 픽셀 그대로 재현한다.
캔버스 1674x912, 그레이 그라데이션(#D9D9D9 -> #737373) 라운드탑 바, 투명 배경.
원본은 그리드선과 y축/x축 제목이 눈금 스케일에서 어긋나 있는데(피그마에서 손으로
옮긴 흔적), 디자인을 그대로 두기 위해 어긋난 위치를 원본 좌표로 하드코딩한다.
replica 검증: scripts/dz_rtt_replica_check.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
from matplotlib.transforms import ScaledTranslation

TOP_N = 22
W, H = 1674, 912                      # 캔버스 (px = pt @ dpi 72)
LEFT, RIGHT, BOTTOM, TOP = 180.043, 1671.0, 733.104, 77.27   # 플롯 영역 (px, top-left 기준)
BAR_W, PITCH, FIRST_C = 37.646, 66.42, 233.067               # 바 폭 / 간격 / 첫 바 중심
SCALE = 7.925                         # y축 px per % (원본 눈금 라벨 간격에서 역산)
YMAX = (BOTTOM - TOP) / SCALE         # 82.76%

# 원본 그리드선 y (px). 눈금 스케일(90px/10%)이 라벨(79.25px/10%)과 어긋나 있으나 원본 유지.
GRID_PX = [641.78, 553.456, 463.456, 373.456, 283.456, 193.456, 103.456]
YLABEL_XY = (19, 226)                 # 원본 "RTT Improvement (%)" 잉크 중심 (px)
XLABEL_XY = (821, 899)                # 원본 "Metro pair (from–to)" 잉크 중심 (px)
TITLE_XY = (180, 32)                  # 원본 타이틀 좌측 baseline (px)

FONT = "assets/font/Pretendard/Pretendard-%s.ttf"
C_TITLE, C_TEXT, C_GRID, C_AXIS = "#CBCBCB", "#777B80", "#4F5458", "#777B80"
BAR_TOP, BAR_BOT = "#D9D9D9", "#737373"   # 바 그라데이션 (위 -> 아래)
BAR_FILL = "#d9d9d9"                      # 후처리에서 url(#dzgrad)로 치환되는 표식
SIZE_TICK, SIZE_XTICK, SIZE_AXIS, SIZE_TITLE = 24, 26.5, 30.5, 34
PAD_Y, PAD_X = 19, 22
XTICK_DX = 3                          # 원본 x 눈금 라벨이 눈금보다 3px 오른쪽에 있다
# 원본 y 눈금 라벨은 바 베이스라인(0%)보다 7.1px 위에 찍혀 있다(피그마에서 라벨
# 그룹이 통째로 밀린 흔적). 그 어긋남까지 그대로 두려고 눈금을 데이터상 +0.9% 민다.
YTICK_SHIFT = (BOTTOM - 726.0) / SCALE

R_X = BAR_W / 2 / PITCH               # 캡 반지름 (x 데이터 단위)
R_Y = BAR_W / 2 / SCALE               # 캡 반지름 (y 데이터 단위)


def load():
    df = pd.read_csv("sources/dz-vs-internet-latency.csv")
    df = df.nlargest(TOP_N, "RTT Improvement (%)")
    return (df["From Metro"] + "–" + df["To Metro"]).tolist(), df["RTT Improvement (%)"].tolist()


def bar(ax, x, v):
    """반원 라운드탑 바. 채움은 SVG 후처리에서 벡터 그라데이션으로 교체된다."""
    t = np.linspace(np.pi, 0, 60)                    # 캡: 화면상 정원이 되도록 반지름 분리
    cap = np.column_stack([x + R_X * np.cos(t), (v - R_Y) + R_Y * np.sin(t)])
    poly = np.vstack([[[x - R_X, 0]], cap, [[x + R_X, 0]]])
    ax.add_patch(Polygon(poly, closed=True, fc=BAR_FILL, ec="none", zorder=3))


def render(labels, values):
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
    ax = fig.add_axes([LEFT / W, 1 - BOTTOM / H, (RIGHT - LEFT) / W, (BOTTOM - TOP) / H])

    x_lo = -(FIRST_C - LEFT) / PITCH
    ax.set_xlim(x_lo, x_lo + (RIGHT - LEFT) / PITCH)
    ax.set_ylim(0, YMAX)

    for i, v in enumerate(values):
        bar(ax, i, v)
    for y_px in GRID_PX:
        ax.axhline((BOTTOM - y_px) / SCALE, color=C_GRID, lw=1.486, zorder=1)

    f_tick = FontProperties(fname=FONT % "Medium", size=SIZE_TICK)
    f_xtick = FontProperties(fname=FONT % "Medium", size=SIZE_XTICK)
    f_axis = FontProperties(fname=FONT % "Medium", size=SIZE_AXIS)
    f_title = FontProperties(fname=FONT % "SemiBold", size=SIZE_TITLE)

    ax.set_yticks([YTICK_SHIFT + 10 * k for k in range(9)])
    ax.set_yticklabels([f"{10 * k}%" for k in range(9)], fontproperties=f_tick, color=C_TEXT)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", rotation_mode="anchor",
                       fontproperties=f_xtick, color=C_TEXT)
    ax.tick_params(axis="y", length=0, pad=PAD_Y, colors=C_TEXT)
    ax.tick_params(axis="x", length=0, pad=PAD_X, colors=C_TEXT)
    nudge = ScaledTranslation(XTICK_DX / 72, 0, fig.dpi_scale_trans)
    for lbl in ax.get_xticklabels():
        lbl.set_transform(lbl.get_transform() + nudge)

    # 축 제목은 원본이 플롯 중심에서 벗어난 위치에 있어 fig 좌표로 직접 배치
    fig.text(YLABEL_XY[0] / W, 1 - YLABEL_XY[1] / H, "RTT Improvement (%)", rotation=90,
             fontproperties=f_axis, color=C_TEXT, alpha=0.9, ha="center", va="center")
    fig.text(XLABEL_XY[0] / W, 1 - XLABEL_XY[1] / H, "Metro pair (from–to)",
             fontproperties=f_axis, color=C_TEXT, alpha=0.9, ha="center", va="center")
    fig.text(TITLE_XY[0] / W, 1 - TITLE_XY[1] / H, f"Round-trip time reduction (%) · top {TOP_N} pairs",
             fontproperties=f_title, color=C_TITLE, ha="left", va="baseline")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set(color=C_AXIS, linewidth=1.981)
    ax.set_axisbelow(True)
    return fig


def save(fig, path):
    """SVG 저장 + 후처리: 원본과 같은 px 캔버스, 바 채움을 벡터 linearGradient로.
    objectBoundingBox 기준이라 각 바가 제 꼭대기 -> 베이스라인 구간의 그라데이션을 갖는다."""
    plt.rcParams["svg.fonttype"] = "path"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="svg", transparent=True)
    grad = ('<defs><linearGradient id="dzgrad" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BAR_TOP}"/>'
            f'<stop offset="1" stop-color="{BAR_BOT}"/></linearGradient></defs>')
    doc = (path.read_text()
           .replace(f'width="{W}pt"', f'width="{W}"')
           .replace(f'height="{H}pt"', f'height="{H}"')
           .replace('version="1.1">', 'version="1.1">\n ' + grad, 1)
           .replace(f"fill: {BAR_FILL}", "fill: url(#dzgrad)"))
    assert "url(#dzgrad)" in doc and "<image" not in doc, "그라데이션 치환 실패"
    path.write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    labels, values = load()
    fig = render(labels, values)
    save(fig, "outputs/charts/dz_rtt_improvement.svg")
    fig.savefig("outputs/charts/dz_rtt_improvement.png", dpi=144, transparent=True)
    print("\n".join(f"{l:>10} {v:5.1f}%" for l, v in zip(labels, values)))
