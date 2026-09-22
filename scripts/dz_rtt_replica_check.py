"""
charts/dz_rtt_improvement.py 의 레이아웃이 피그마 원본과 일치하는지 검증한다.

원본(Group 1991501171.svg의 백업)에서 바 좌표를 읽어 옛 데이터를 역산하고,
그 데이터로 렌더한 replica를 원본과 픽셀 비교한다. 데이터가 아니라 레이아웃
(눈금/그리드/축 제목/바 지오메트리)이 어긋나면 잉크 bbox 차이로 드러난다.

    .venv/bin/python scripts/dz_rtt_replica_check.py <원본.svg>
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "charts")
from PIL import Image  # noqa: E402

import dz_rtt_improvement as dz  # noqa: E402

OLD_LABELS = ["lon–osl", "lax–slc", "hkg–tyo", "muc–sxb", "ams–dub", "mad–mrs", "chi–pit",
              "nyc–yto", "fra–tyo", "mrs–sxb", "sea–slc", "fra–osl", "mrs–sao", "fra–muc",
              "nyc–ymq", "fra–sxb", "fra–prg", "chi–slc", "ams–fra", "muc–waw", "sqq–sto",
              "nyc–was"]


def bar_tops(svg):
    """원본 SVG의 바 path에서 캡 꼭대기 y(px)를 읽는다."""
    return [float(re.search(r"C[\d.]+ [\d.]+ [\d.]+ ([\d.]+)", d).group(1))
            for d in re.findall(r'<path d="(M[^"]+)" fill="url', Path(svg).read_text())]


def rasterize(svg, png):
    subprocess.run(["rsvg-convert", "-b", "white", svg, "-o", png], check=True)
    return Image.open(png).convert("L")


def ink(im, box, thr=245):
    """box 영역 안 잉크의 bbox. 없으면 None."""
    px = im.load()
    xs, ys = [], []
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if px[x, y] < thr:
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def main(orig_svg):
    tmp = Path(subprocess.run(["mktemp", "-d"], capture_output=True, text=True).stdout.strip())
    values = [(dz.BOTTOM - t) / dz.SCALE for t in bar_tops(orig_svg)]
    assert len(values) == len(OLD_LABELS), f"바 {len(values)}개 != 라벨 {len(OLD_LABELS)}개"

    dz.save(dz.render(OLD_LABELS, values), tmp / "replica.svg")
    a = rasterize(orig_svg, str(tmp / "orig.png"))
    b = rasterize(str(tmp / "replica.svg"), str(tmp / "replica.png"))
    assert a.size == b.size == (dz.W, dz.H), f"캔버스 불일치: {a.size} vs {b.size}"

    regions = {                              # 원본 기준 각 요소를 감싸는 영역
        "title":   (100, 0, 900, 60),
        "y ticks": (60, 60, 178, 800),
        "y label": (0, 60, 60, 800),
        "x label": (400, 860, 1300, 912),
        "bars+grid": (180, 60, 1674, 745),
        "x ticks": (150, 745, 1674, 880),
    }
    print(f"{'region':<10} {'원본 잉크 bbox':<26} {'replica':<26} delta")
    worst = 0
    for name, box in regions.items():
        ia, ib = ink(a, box), ink(b, box)
        d = tuple(q - p for p, q in zip(ia, ib))
        worst = max(worst, max(abs(v) for v in d))
        print(f"{name:<10} {str(ia):<26} {str(ib):<26} {d}")
    # 폰트 메트릭 차이로 잉크 끝점은 몇 px 흔들린다. 배치가 틀어지면 훨씬 크게 벌어진다.
    tol = 5
    print(f"\n최대 어긋남: {worst}px (허용 {tol}px)  {'OK' if worst <= tol else '레이아웃 불일치'}")
    return 0 if worst <= tol else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
