# Pie / Donut Chart (Four Pillars 표준)

파이/도넛 요청은 **항상 이 형식**으로 그린다: 가운데가 뚫린 도넛 + 슬라이스
사이 다크 구분선 + 슬라이스마다 외부 리더라인(곧은 직선)과 끝에 컬러 도트 +
도트 옆/위 2줄 라벨(이름 / 퍼센트). 라벨은 슬라이스 각도 순서대로 분산 배치해
선이 도넛이나 다른 선과 겹치지 않게 한다.

> full pie(가운데 안 뚫린)도 같은 라벨 방식을 쓰되 `donut_width`를 키워
> `radius`와 같게(=원판) 두면 된다. 기본은 도넛.

## 핵심 규칙

- **도넛 + 외부 리더라벨** 형식 고정. 슬라이스 안에 % 박지 않는다.
- **슬라이스 구분선**은 배경색(`#141414`)으로 얇게.
- **라벨 = 컬러 도트 + 2줄**(이름 밝은 회색 / 퍼센트 연회색). 도트와 글자 사이 간격 확보.
- **분산 배치**: 상단(작은 슬라이스)은 가로로 펼치고, 좌/우는 세로 컬럼. 라벨
  순서 = 슬라이스 각도 순서로 맞춰 선이 교차하지 않게 한다.
- 선이 도넛/다른 선과 겹치면 해당 라벨에 **꺾임점(elbow)**을 줘 우회시킨다.
- 작은 슬라이스(예: <0.3%)들은 `Other`로 묶어 라벨 혼잡을 줄인다.
- 차트에 제목/범례/출처 넣지 않음, **투명 배경** 유지(four-pillars 공통 규칙).

## 구현: `config.donut_leader_labels()`

`.claude/skills/design/four-pillars/config.py` 의 표준 함수를 쓴다.

```python
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import donut_leader_labels, auto_label_pos, save_chart

df = pd.read_csv("outputs/data/<topic>.csv")   # columns: token, pct, color

# 라벨/도트 위치. 처음엔 auto_label_pos 로 시작해 결과 보고 손으로 미세조정.
LABEL_POS = {
    "UNIBTC":  (+1.34, -0.55, "right"),   # (dot_x, dot_y, mode)
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
    # "WEETH": [(-1.05, 0.52)],   # 슬라이스 → (-1.05,0.52) → 도트 로 각지게 우회
}

fig, ax = donut_leader_labels(
    values=df["pct"].tolist(),
    labels=df["token"].tolist(),
    colors=df["color"].tolist(),
    label_pos=LABEL_POS,   # None 이면 auto_label_pos 로 자동(시작점)
    elbow=ELBOW,
    start_angle=90,
)
save_chart(fig, "<topic>", "outputs/charts/<protocol>/<category>")
```

## 함수 시그니처

```python
donut_leader_labels(
    values, labels, colors,        # 슬라이스 값/이름/색 (큰→작은 정렬 권장)
    label_pos=None,                # {label: (dot_x, dot_y, mode)}  None=auto
    elbow=None,                    # {label: [(x,y),...]}  선 꺾임점(겹침 우회)
    start_angle=90, donut_width=0.42, radius=1.0,
    label_gap=0.16, top_gap=0.16,  # 도트-글자 간격(좌우 가로 / 상단 세로)
    line_width=1.5, dot_size=46,
    value_to_pct=True,             # 라벨 %를 value/합계로 계산
    ...                            # 폰트/색/figsize/xlim/ylim 도 조정 가능
) -> (fig, ax)
```

### mode

| mode | 글자 정렬 | 도트 위치 | 용도 |
|------|----------|----------|------|
| `left` | 오른쪽정렬 | 글자 오른쪽 | 도넛 왼쪽 슬라이스 |
| `right` | 왼쪽정렬 | 글자 왼쪽 | 도넛 오른쪽 슬라이스 |
| `top` | 중앙정렬(도트 위) | 글자 아래 | 상단에 펼치는 작은 슬라이스 |

## 배치 절차

1. `auto_label_pos(values, labels, start_angle)` 로 기본 위치를 받아 렌더.
2. 선이 도넛을 가로지르거나 서로 겹치면:
   - 라벨이 전부 한쪽에 몰려 있으면 슬라이스가 그쪽을 바라보도록
     `start_angle`을 돌리거나, 라벨을 슬라이스 근처(분산)로 옮긴다.
   - 그래도 겹치는 선은 `ELBOW`로 꺾어 우회시킨다.
3. 도트와 글자가 붙으면 `label_gap` / `top_gap` 을 키운다.

## 데이터 CSV 형식

```csv
token,pct,color
UNIBTC,64.65,#3F8BD7
USDC,10.38,#9FC131
...
```

`color`는 브랜드/구분 색. `pct`는 share(%) 또는 raw value(`value_to_pct=True`면
자동으로 합계 대비 %로 환산).

## 예시 산출물

`charts/cap_tvl_token_breakdown.py` → `outputs/charts/cap/tvl/cap_tvl_token_breakdown.{png,svg}`
