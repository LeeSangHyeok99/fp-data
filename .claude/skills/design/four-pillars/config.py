"""
Four Pillars Design Configuration
matplotlib 차트 스타일 설정
"""

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# =============================================================================
# 색상 정의
# =============================================================================
COLORS = {
    "background": "#141414",
    "text": "#d1d4dc",
    "text_secondary": "#787b86",
    "grid": "#787b86",
}

# 차트 시리즈 색상
SERIES_COLORS = [
    "#5470c6",  # 블루
    "#91cc75",  # 그린
    "#fac858",  # 옐로우
    "#ee6666",  # 레드
    "#73c0de",  # 라이트 블루
    "#3ba272",  # 틸
    "#fc8452",  # 오렌지
    "#9a60b4",  # 퍼플
    "#ea7ccc",  # 핑크
]

# 증감 표시용
POSITIVE_COLOR = "#26a69a"
NEGATIVE_COLOR = "#ef5350"


# =============================================================================
# 폰트 설정
# =============================================================================
def _find_font(rel):
    """폰트 파일을 여러 후보 루트에서 찾는다 (assets 위치가 옮겨져도 동작)."""
    roots = [Path("assets/font"), Path("charts/assets/font"),
             Path.home() / "Library/Fonts"]
    for root in roots:
        # 계층형 경로(assets/font/Pretendard/..)와 플랫형(~/Library/Fonts/..) 둘 다 시도
        for cand in (root / rel, root / Path(rel).name):
            if cand.exists():
                return cand
    return None


def setup_font():
    """Pretendard Bold 폰트 설정 (로컬 assets), 없으면 SUIT, 그다음 Arial 폴백"""
    pretendard = _find_font("Pretendard/Pretendard-Bold.ttf")
    suit = _find_font("SUIT/SUIT-ttf/SUIT-Bold.ttf")
    if pretendard:
        fm.fontManager.addfont(str(pretendard))
        plt.rcParams["font.family"] = "Pretendard"
    elif suit:
        fm.fontManager.addfont(str(suit))
        plt.rcParams["font.family"] = "SUIT"
    else:
        plt.rcParams["font.family"] = "Arial"

    plt.rcParams["font.weight"] = "bold"


# =============================================================================
# 차트 크기
# =============================================================================
# Default: 1600 x 700 px @ 150 DPI = 10.67 x 4.67 inch
DEFAULT_FIGSIZE = (10.67, 4.67)

FIGURE_SIZES = {
    "line": DEFAULT_FIGSIZE,
    "area": DEFAULT_FIGSIZE,
    "stacked": DEFAULT_FIGSIZE,
    "stacked_bar": DEFAULT_FIGSIZE,
    "bar": DEFAULT_FIGSIZE,
    "horizontal_bar": DEFAULT_FIGSIZE,
    "pie": DEFAULT_FIGSIZE,
    "donut": DEFAULT_FIGSIZE,
}

DPI = 150

# =============================================================================
# 축 설정
# =============================================================================
AXIS_CONFIG = {
    "y_label": {
        "fontsize": 20,
        "fontweight": "bold",
        "labelpad": 20,
        "color": COLORS["text_secondary"],
    },
    "y_tick": {
        "fontsize": 24,
        "fontweight": "bold",
        "pad": 15,
        "length": 0,
        "color": COLORS["text_secondary"],
        "max_ticks": 5,  # Y축 틱 최대 5개
    },
    "x_tick": {
        "fontsize": 22,
        "fontweight": "bold",
        "pad": 10,
        "rotation": 45,
        "ha": "right",
        "length": 6,
        "width": 1,
        "color": COLORS["text_secondary"],
    },
}

# =============================================================================
# 그리드 설정
# =============================================================================
GRID_CONFIG = {
    "color": COLORS["grid"],
    "alpha": 0.5,
    "linestyle": (0, (3.7, 1.6)),  # 점선 (dash, gap)
    "linewidth": 1.0,
}


# =============================================================================
# 스타일 적용 함수
# =============================================================================
def apply_style(fig, ax, chart_type="line"):
    """Four Pillars 스타일을 차트에 적용"""

    # 배경 투명
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # 그리드
    ax.grid(
        True,
        axis="y",
        color=GRID_CONFIG["color"],
        alpha=GRID_CONFIG["alpha"],
        linestyle=GRID_CONFIG["linestyle"],
        linewidth=GRID_CONFIG["linewidth"],
    )
    ax.set_axisbelow(True)

    # 축 spine 숨김
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Y축 설정
    ax.yaxis.label.set_fontsize(AXIS_CONFIG["y_label"]["fontsize"])
    ax.yaxis.label.set_fontweight(AXIS_CONFIG["y_label"]["fontweight"])
    ax.yaxis.labelpad = AXIS_CONFIG["y_label"]["labelpad"]
    ax.yaxis.label.set_color(AXIS_CONFIG["y_label"]["color"])

    ax.tick_params(
        axis="y",
        labelsize=AXIS_CONFIG["y_tick"]["fontsize"],
        pad=AXIS_CONFIG["y_tick"]["pad"],
        length=AXIS_CONFIG["y_tick"]["length"],
        colors=AXIS_CONFIG["y_tick"]["color"],
    )

    # X축 설정
    ax.tick_params(
        axis="x",
        labelsize=AXIS_CONFIG["x_tick"]["fontsize"],
        pad=AXIS_CONFIG["x_tick"]["pad"],
        rotation=AXIS_CONFIG["x_tick"]["rotation"],
        colors=AXIS_CONFIG["x_tick"]["color"],
        length=AXIS_CONFIG["x_tick"]["length"],
        width=AXIS_CONFIG["x_tick"]["width"],
    )
    plt.setp(ax.xaxis.get_majorticklabels(), ha=AXIS_CONFIG["x_tick"]["ha"])

    # 레이아웃
    fig.tight_layout()


def create_figure(chart_type="line"):
    """차트 타입에 맞는 Figure 생성"""
    setup_font()
    figsize = FIGURE_SIZES.get(chart_type, (18, 10))
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    return fig, ax


def save_chart(fig, filename, output_dir="outputs/charts", tight=True):
    """PNG와 SVG로 저장

    tight=False면 bbox_inches를 쓰지 않는다. 픽셀 격자에 맞춰 배치한 차트
    (pixel_grid_figure)는 tight 크롭이 소수 픽셀로 밀려 정렬이 깨진다.
    """
    bbox = "tight" if tight else None
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # PNG 저장 (투명 배경)
    png_path = output_path / f"{filename}.png"
    fig.savefig(
        png_path,
        dpi=DPI,
        facecolor="none",
        edgecolor="none",
        bbox_inches=bbox,
        transparent=True,
    )

    # SVG 저장 (투명 배경)
    svg_path = output_path / f"{filename}.svg"
    fig.savefig(
        svg_path,
        format="svg",
        facecolor="none",
        edgecolor="none",
        bbox_inches=bbox,
        transparent=True,
    )

    return str(png_path), str(svg_path)


# =============================================================================
# 비주얼 이펙트 함수
# =============================================================================
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath


def gradient_rounded_bar(ax, x_center, width, height, color, alpha=0.95, floor=0.15,
                         round_top=True, y0=0.0, ceil=1.0):
    """그라데이션 바. 아래는 어둡고 위로 갈수록 밝아진다.

    round_top=True면 상단에 라운드(반원) 마감, False면 평평한 마감.

    Args:
        ax: matplotlib Axes
        x_center: 바 중심 x좌표
        width: 바 너비
        height: 바 상단 y좌표 (None이면 무시)
        color: 바 상단 색상 (hex)
        alpha: 투명도
        floor: 그라데이션 바닥 밝기(0~1). 낮을수록 어둡다.
        round_top: 상단 라운드 마감 여부
        y0: 바 하단 y좌표. 스택 바에서 세그먼트마다 자기 구간에만 그라데이션을
            주려면 아래 밴드의 누적합을 넘긴다. 기본 0이면 바닥부터 그린다.
        ceil: 상단 밝기 배수. 1.0이면 위가 원색. floor=0.85, ceil=1.15처럼 주면
            원색이 그라데이션의 중간에 오고 위는 살짝 밝아진다 (채널은 1로 클립).
    """
    import pandas as pd

    if pd is not None and pd.isna(height):
        return
    if height is None or height <= y0:
        return

    x_left = x_center - width / 2
    x_right = x_center + width / 2

    if round_top:
        # 작은 라운드 코너(반원 아님). 픽셀 기준으로 잡아 축 종횡비와 무관하게
        # 일정한 크기로 보이게 한다. 호출 전 xlim/ylim을 확정해 둘 것.
        corner_px = 7.0
        o = ax.transData.transform((0.0, 0.0))
        ux = ax.transData.transform((1.0, 0.0))[0] - o[0]
        uy = ax.transData.transform((0.0, 1.0))[1] - o[1]
        rx = min(corner_px / abs(ux), width * 0.45) if ux else width * 0.2
        seg_h = height - y0
        ry = min(corner_px / abs(uy), seg_h * 0.45) if uy else seg_h * 0.05
        t_r = np.linspace(0, np.pi / 2, 12)
        t_l = np.linspace(np.pi / 2, np.pi, 12)
        verts = [(x_left, y0), (x_right, y0), (x_right, height - ry)]
        verts += [((x_right - rx) + rx * np.cos(t), (height - ry) + ry * np.sin(t)) for t in t_r]
        verts += [((x_left + rx) + rx * np.cos(t), (height - ry) + ry * np.sin(t)) for t in t_l]
        verts.append((x_left, y0))
    else:
        verts = [(x_left, y0), (x_right, y0), (x_right, height),
                 (x_left, height), (x_left, y0)]

    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    path = MPath(verts, codes)
    clip_patch = PathPatch(
        path, facecolor="none", edgecolor="none", transform=ax.transData
    )
    ax.add_patch(clip_patch)

    # 수직 그라데이션 이미지
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = floor + (ceil - floor) * (frac**0.5 if ceil == 1.0 else frac)
        gradient[i, 0] = [min(r * factor, 1), min(g * factor, 1), min(b * factor, 1), alpha]

    im = ax.imshow(
        gradient,
        aspect="auto",
        origin="lower",
        extent=[x_left, x_right, y0, height],
        zorder=3,
        interpolation="bilinear",
    )
    im.set_clip_path(clip_patch)


def gradient_barh(ax, rect, color, floor=0.80, alpha=0.95):
    """가로 막대 그라데이션. 원점 쪽이 어둡고 끝으로 갈수록 밝아진다.

    gradient_rounded_bar를 가로로 눕힌 것. floor 규약(같은 색상 안에서 어두운 톤
    -> 원색)이 같아서 세로 막대 차트들과 톤이 맞는다.

    ax.barh()가 돌려준 rect를 그대로 넘기면 된다. rect는 클립 마스크 역할만 하고
    면은 비운다.

    주의: imshow가 축을 이미지 경계에 딱 맞춰버려서 맨 위/아래 막대가 잘린다.
    호출한 쪽에서 ax.set_ylim(n - 0.5, -0.5)로 여백을 되돌려 줄 것.

    Args:
        ax: matplotlib Axes
        rect: ax.barh()가 반환한 막대 하나 (Rectangle)
        color: 막대 색상 (hex)
        floor: 원점 쪽 밝기(0~1). 1에 가까울수록 그라데이션 폭이 좁다.
        alpha: 투명도
    """
    r, g, b = mcolors.to_rgb(color)
    factor = floor + (1.0 - floor) * np.linspace(0, 1, 256) ** 0.5
    gradient = np.stack(
        [r * factor, g * factor, b * factor, np.full(256, alpha)], axis=-1
    )[None, :, :]
    rect.set_facecolor("none")
    ax.imshow(
        gradient,
        aspect="auto",
        interpolation="bilinear",
        zorder=rect.get_zorder(),
        extent=[rect.get_x(), rect.get_x() + rect.get_width(),
                rect.get_y(), rect.get_y() + rect.get_height()],
    )


def area_glow(ax, x, y, color, n_layers=50, max_alpha=0.18, power=2.5):
    """라인 근처에 집중되는 글로우 에어리어 필.

    라인에 가까울수록 강하고, 아래로 갈수록 투명해진다.

    Args:
        ax: matplotlib Axes
        x: x 데이터 (array-like)
        y: y 데이터 (array-like)
        color: 글로우 색상 (hex)
        n_layers: 레이어 수 (높을수록 부드러움)
        max_alpha: 최대 투명도
        power: 글로우 집중도 (높을수록 라인 근처에 집중)
    """
    for i in range(n_layers):
        frac = i / n_layers
        alpha = max_alpha * (frac**power)
        lower = y * frac
        upper = y * (frac + 1 / n_layers)
        ax.fill_between(
            x, lower, upper, color=color, alpha=alpha, linewidth=0, zorder=2
        )


def pixel_grid_figure(n_days, day_px, ax_h=530, left_px=130, right_px=12,
                      bottom_px=150, top_px=20):
    """하루가 정확히 day_px 픽셀이 되는 Figure/Axes를 만든다.

    일별 막대 차트에서 하루 폭이 소수 픽셀이면 막대와 간격이 매번 다른 위치에
    반올림돼 굵기가 들쭉날쭉해 보인다. 축 폭을 일수 x day_px로 역산해 막대가
    정수 픽셀 경계에 앉게 한다.

    apply_style()이 tight_layout을 부르므로, 스타일 적용 뒤에 반환된 geom으로
    ax.set_position(geom)을 호출하고 save_chart(..., tight=False)로 저장할 것.

    Returns: (fig, ax, geom)
    """
    setup_font()
    ax_w = n_days * day_px
    fig_w = left_px + ax_w + right_px
    fig_h = top_px + ax_h + bottom_px
    fig, ax = plt.subplots(figsize=(fig_w / DPI, fig_h / DPI), dpi=DPI)
    geom = [left_px / fig_w, bottom_px / fig_h, ax_w / fig_w, ax_h / fig_h]
    return fig, ax, geom


def gradient_bars(ax, xs, values, color, day_px, bar_px, floor=0.62,
                  bottoms=None, per_bar=False):
    """막대를 세로 그라데이션 한 장 + 막대 실루엣 클립으로 그린다.

    막대마다 imshow를 부르면 수백 장이 되므로 그라데이션 이미지 한 장을
    막대 모양 path로 클립한다. floor는 바닥 밝기(1에 가까울수록 약한 효과).
    xs는 날짜(일별) 또는 숫자 인덱스(월별처럼 간격이 불규칙한 경우).
    bottoms를 주면 스택 막대의 세그먼트로 그린다.
    xlim/ylim을 확정한 뒤 호출할 것.

    Args:
        ax: matplotlib Axes
        xs: 막대 중심 x (datetime 시퀀스 또는 숫자 시퀀스)
        values: 막대 높이 (bottoms를 주면 세그먼트 높이)
        color: 막대 색상 (hex)
        day_px: x 한 칸의 픽셀 폭 (pixel_grid_figure에 넘긴 값)
        bar_px: 막대 픽셀 폭
        floor: 바닥 밝기(0~1)
        bottoms: 세그먼트 하단 y (스택 막대용). None이면 0부터.
        per_bar: True면 막대(세그먼트)마다 자기 높이에 맞춘 그라데이션을 준다.
            막대가 수십 개 수준일 때 쓴다. False면 축 전체 기준 한 장(기본).
    """
    import matplotlib.dates as mdates

    half = (bar_px / day_px) / 2  # x 한 칸 기준 반폭
    if bottoms is None:
        bottoms = np.zeros(len(values))
    verts, codes = [], []
    for d, v, b in zip(xs, values, bottoms):
        x = d if isinstance(d, (int, float, np.integer, np.floating)) \
            else mdates.date2num(d)
        left, right = x - half, x + half
        top = b + v
        verts += [(left, b), (right, b), (right, top), (left, top), (left, b)]
        codes += [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO,
                  MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor="none", edgecolor="none",
                     transform=ax.transData)
    ax.add_patch(clip)

    r, g, b_ = mcolors.to_rgb(color)
    factor = floor + (1 - floor) * np.linspace(0, 1, 256) ** 0.5
    gradient = np.stack([r * factor, g * factor, b_ * factor,
                         np.ones(256)], axis=-1)[:, None, :]

    if per_bar:
        # 세그먼트마다 자기 구간에 그라데이션을 채운다 (path 5개씩 끊어 클립)
        for i in range(len(verts) // 5):
            (left, bot), _, (right, top), _, _ = verts[i * 5:i * 5 + 5]
            if top <= bot:
                continue
            seg = PathPatch(MPath(verts[i * 5:i * 5 + 5], codes[i * 5:i * 5 + 5]),
                            facecolor="none", edgecolor="none",
                            transform=ax.transData)
            ax.add_patch(seg)
            im = ax.imshow(gradient, aspect="auto", origin="lower", zorder=2,
                           interpolation="bilinear",
                           extent=[left, right, bot, top])
            im.set_clip_path(seg)
        return

    img = ax.imshow(gradient, aspect="auto", origin="lower", zorder=2,
                    interpolation="bilinear",
                    extent=[*ax.get_xlim(), 0, ax.get_ylim()[1]])
    img.set_clip_path(clip)


def endpoint_dot(ax, x, y, color, size=50):
    """시리즈 끝점에 원형 마커를 찍는다.

    Args:
        ax: matplotlib Axes
        x: x 좌표 (scalar)
        y: y 좌표 (scalar)
        color: 마커 색상
        size: 마커 크기
    """
    # clip_on=False: xlim 끝에 찍히는 마커가 축 경계에 잘리지 않게
    ax.scatter(x, y, color=color, s=size, zorder=5, edgecolors="none",
               clip_on=False)


# =============================================================================
# Four Pillars 표준 파이/도넛 (외부 리더라벨)
# =============================================================================
# 파이/도넛 요청은 항상 이 형식으로 그린다:
#   · 도넛(가운데 구멍) + 슬라이스 사이 다크 구분선
#   · 슬라이스마다 외부 리더라인(곧은 직선) + 끝에 컬러 도트
#   · 도트 옆/위에 2줄 라벨(이름 / 퍼센트), 도트와 글자 사이 간격 확보
#   · 라벨은 슬라이스 각도 순서대로 분산 배치(상단 펼침 / 좌우 컬럼)해 선이
#     도넛이나 다른 선과 겹치지 않게 한다.
#   · 라벨 위치는 label_pos 로 손으로 조정, 필요하면 elbow 로 선을 꺾어 우회.
#
# 차트 스타일 규칙(제목/범례/출처 차트에 넣지 않음, 투명 배경)은 그대로 유지.

def auto_label_pos(values, labels, start_angle=90, counterclock=False):
    """슬라이스 각도 기준으로 분산된 라벨 위치 기본값을 만든다(시작점).

    상단(60~120°)은 가로로 펼치고, 좌/우는 세로 컬럼으로 둔 뒤 최소 간격을
    확보한다. 완벽하진 않으니 결과를 보고 label_pos 로 미세조정하는 용도.

    Returns: {label: (dot_x, dot_y, mode)}  mode: "left"|"right"|"top"
    """
    total = float(sum(values))
    # 각 슬라이스 midangle 계산 (matplotlib pie 와 동일 규칙)
    ang = {}
    acc = start_angle
    for lab, v in zip(labels, values):
        sweep = v / total * 360.0
        mid = acc - sweep / 2 if not counterclock else acc + sweep / 2
        ang[lab] = mid % 360
        acc = acc - sweep if not counterclock else acc + sweep

    def yx(a):
        r = np.deg2rad(a)
        return np.cos(r), np.sin(r)

    top, left, right = [], [], []
    for lab in labels:
        a = ang[lab]
        if 58 <= a <= 122:
            top.append(lab)
        elif 122 < a < 238:
            left.append(lab)
        else:
            right.append(lab)

    pos = {}
    # 상단: x 를 각도순으로 펼침(코사인 큰 쪽=오른쪽), 같은 높이
    top.sort(key=lambda l: yx(ang[l])[0])
    if top:
        xs = np.linspace(-1.05, 1.05, len(top)) if len(top) > 1 else [0.0]
        for lab, x in zip(top, xs):
            pos[lab] = (float(x), 1.42, "top")
    # 좌/우: y = sin*1.3, 최소 간격 0.34
    for grp, mode, sign in ((left, "left", -1), (right, "right", 1)):
        grp.sort(key=lambda l: yx(ang[l])[1], reverse=True)
        ys = [yx(ang[l])[1] * 1.3 for l in grp]
        for i in range(1, len(ys)):
            if ys[i] > ys[i - 1] - 0.34:
                ys[i] = ys[i - 1] - 0.34
        for lab, y in zip(grp, ys):
            pos[lab] = (sign * 1.42, float(y), mode)
    return pos


def donut_leader_labels(
    values, labels, colors, label_pos=None, elbow=None,
    start_angle=90, donut_width=0.42, radius=1.0,
    label_gap=0.16, top_gap=0.16, line_width=1.5, dot_size=46,
    name_fs=15, pct_fs=14, top_name_fs=14, top_pct_fs=13,
    text_color="#c7ccd3", dim_color="#8b9099", sep_color="#141414",
    figsize=(8.4, 8.4), xlim=(-2.0, 2.0), ylim=(-1.5, 1.9), value_to_pct=True,
    sublabels=None, gradient=False, angled=False, angle_run=0.34, level=(),
):
    """Four Pillars 표준 도넛(외부 리더라벨)을 그린다.

    Args:
        values, labels, colors : 슬라이스 값/이름/색 (같은 길이, 큰→작은 정렬 권장)
        label_pos : {label: (dot_x, dot_y, mode)} 라벨/도트 위치. None이면 auto.
                    dot_y가 None이면 슬라이스 중앙 높이에 맞춰 리더선이 수평이 되고,
                    "radial"이면 도트를 슬라이스 반지름 연장선 위에 올린다(꺾임 없는 수직선).
                    mode: "left"(글자 우정렬,도트 좌) "right"(글자 좌정렬,도트 우)
                          "top"(글자 도트 위, 중앙정렬)
        elbow : {label: [(x,y),...]} 선이 거쳐가는 꺾임점(선택). 겹침 우회용.
        value_to_pct : True면 라벨 퍼센트를 value/합계로 계산. False면 value 그대로(%).
        sublabels : {label: str} 서브라벨 텍스트 직접 지정(예: "$2.3B"). 주면 % 대신 사용.
        angled : True면 리더선을 곧은 사선 대신 직각으로 꺾는다. 라벨 쪽은 도트와
                 같은 높이(top 모드는 같은 x)로 나가고, 슬라이스 쪽만 사선이 된다.
                 라벨 목록을 주면 그 라벨만 꺾고 나머지는 직선.
        angle_run : 꺾임점까지의 직선 구간 길이(도넛 반지름 기준). {label: 길이}
                    딕트를 주면 라벨별로 다르게 뻗는다(기본 0.34).
        level : 리더선을 도트 높이에서 호에 바로 붙이는 라벨 목록. 웨지가 넓어
                도트 높이도 같은 웨지 안이면 이게 곧 호에 수직인 수평선이 된다.
        gradient : True면 각 웨지에 상단 밝음→하단 어두움 광택 그라데이션. 0~1 값을
                   주면 그 세기로 약하게 준다(True == 1.0).
    Returns: (fig, ax)
    """
    setup_font()
    if label_pos is None:
        label_pos = auto_label_pos(values, labels, start_angle)
    elbow = elbow or {}

    total = float(sum(values))
    pct_of = {lab: (v / total * 100 if value_to_pct else v)
              for lab, v in zip(labels, values)}
    col_of = dict(zip(labels, colors))

    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    wedges, _ = ax.pie(
        values, colors=colors, startangle=start_angle, counterclock=False,
        radius=radius,
        wedgeprops=dict(width=donut_width, edgecolor=sep_color,
                        linewidth=2.4, antialiased=True),
    )

    if gradient:
        # 웨지별 세로 그라데이션(상단 밝음→하단 어두움) = 광택 3D 느낌.
        grad = np.repeat(np.linspace(0, 1, 256).reshape(-1, 1), 2, axis=1)
        g = 1.0 if gradient is True else float(gradient)   # 광택 세기(0~1)
        for w, c in zip(wedges, colors):
            base = np.array(mcolors.to_rgb(c))
            lo = base * (1 - 0.18 * g)          # 하단(어둡게)
            hi = base + (1 - base) * (0.32 * g)  # 상단(밝게)
            cmap = mcolors.LinearSegmentedColormap.from_list("g", [lo, hi])
            im = ax.imshow(grad, extent=[-radius, radius, -radius, radius],
                           origin="lower", cmap=cmap, aspect="auto",
                           interpolation="bilinear", zorder=1)
            im.set_clip_path(w)
            w.set_facecolor("none")
            w.set_zorder(1.5)

    slice_edge = {}
    for w, lab in zip(wedges, labels):
        a = np.deg2rad((w.theta1 + w.theta2) / 2)
        slice_edge[lab] = (np.cos(a) * radius, np.sin(a) * radius)

    for lab, (xd, yd, mode) in label_pos.items():
        if lab not in slice_edge:
            continue
        ex, ey = slice_edge[lab]
        col = col_of[lab]
        bend = list(elbow.get(lab, []))
        ang = angled if isinstance(angled, bool) else lab in angled
        run = angle_run.get(lab, 0.34) if isinstance(angle_run, dict) else angle_run
        if lab in level:    # 도트 높이에서 호에 수평으로 붙인다
            ex = np.sign(xd) * np.sqrt(max(radius ** 2 - yd ** 2, 0.0))
            ey = yd
        elif yd == "radial":  # 반지름 연장선 위에 도트 = 꺾임 없이 호에 수직인 직선
            yd = ey * xd / ex
        elif yd is None:
            # 리더선 끝을 수평으로 스냅. angled면 슬라이스에서 반지름 방향으로
            # 곧게 뻗은 뒤 그 높이에서 꺾고, 아니면 슬라이스 중앙 높이 그대로.
            if ang and not bend:
                bend = [(ex * (1 + run / radius), ey * (1 + run / radius))]
                yd = bend[0][1]
            else:
                yd = ey
        elif ang and not bend:
            if mode == "top":
                if yd - run > ey:
                    bend = [(xd, yd - run)]
            else:
                dirx = 1 if mode == "left" else -1
                bx = xd + dirx * run
                if (bx - ex) * dirx < 0:
                    bend = [(bx, yd)]
        pts = [(ex, ey)] + bend + [(xd, yd)]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col,
                linewidth=line_width, zorder=2,
                solid_capstyle="round", solid_joinstyle="round")
        ax.scatter([xd], [yd], s=dot_size, color=col, zorder=3, edgecolors="none")

        name = lab
        pct = sublabels[lab] if sublabels else f"{pct_of[lab]:.2f}%"
        if mode == "top":
            ax.annotate(pct, xy=(xd, yd + top_gap), ha="center", va="center",
                        fontsize=top_pct_fs, fontweight="bold",
                        color=dim_color, zorder=4)
            ax.annotate(name, xy=(xd, yd + top_gap + 0.11), ha="center",
                        va="center", fontsize=top_name_fs, fontweight="bold",
                        color=text_color, zorder=4)
        else:
            ha = "right" if mode == "left" else "left"
            tx = xd + (-label_gap if mode == "left" else label_gap)
            ax.annotate(name, xy=(tx, yd + 0.085), ha=ha, va="center",
                        fontsize=name_fs, fontweight="bold",
                        color=text_color, zorder=4)
            ax.annotate(pct, xy=(tx, yd - 0.085), ha=ha, va="center",
                        fontsize=pct_fs, fontweight="bold",
                        color=dim_color, zorder=4)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig, ax


# =============================================================================
# 사용 예시
# =============================================================================
"""
from config import (create_figure, apply_style, save_chart,
                    SERIES_COLORS, gradient_rounded_bar, area_glow, endpoint_dot)

# 그라데이션 라운드 바
gradient_rounded_bar(ax, x_center=0, width=0.17, height=11.77, color='#C9A84C')

# 에어리어 글로우
area_glow(ax, dates, gold_oi, color='#C9A84C')

# 끝점 도트
endpoint_dot(ax, dates.iloc[-1], gold_oi.iloc[-1], color='#C9A84C')
"""


def band_gradient(ax, x, lower, upper, color, spread=0.28, alpha=0.98):
    """스택 에어리어 밴드 하나를 세로 그라데이션으로 채운다.

    밴드 한가운데가 정확히 `color`(= 범례에 쓰는 hex)이고, 아래로 갈수록 어두워지고
    위로 갈수록 흰색 쪽으로 옅어진다. 범례 스와치와 밴드 색이 어긋나지 않게 하려면
    이 규약을 유지할 것. 스택 밴드는 imshow 클립으로 칠하므로 x는 숫자여야 한다
    (날짜면 mdates.date2num).

    Args:
        ax: matplotlib Axes
        x: x 좌표 배열 (numeric)
        lower: 밴드 하단 y 배열
        upper: 밴드 상단 y 배열
        color: 브랜드/범례 컬러 (hex). 밴드 중앙이 이 색이 된다.
        spread: 위아래로 벌리는 폭 (0~1). 클수록 그라데이션이 세다.
        alpha: 투명도
    """
    x = np.asarray(x, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)

    verts = list(zip(x, lower)) + list(zip(x[::-1], upper[::-1]))
    verts.append(verts[0])
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor="none", edgecolor="none",
                     transform=ax.transData)
    ax.add_patch(clip)

    base = np.array(mcolors.to_rgb(color))
    t = np.linspace(-1.0, 1.0, 256)[:, None] * spread
    rgb = np.where(t < 0, base[None, :] * (1 + t), base[None, :] * (1 - t) + t)
    grad = np.concatenate([rgb, np.full((256, 1), alpha)], axis=1)[:, None, :]

    y0, y1 = float(lower.min()), float(upper.max())
    if y1 <= y0:
        return
    im = ax.imshow(grad, aspect="auto", origin="lower",
                   extent=[x.min(), x.max(), y0, y1], zorder=2,
                   interpolation="bilinear")
    im.set_clip_path(clip)
