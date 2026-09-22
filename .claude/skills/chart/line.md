# Line Chart

라인 차트 생성 모듈

## Signature

```python
def create_line_chart(request: ChartRequest) -> ChartResponse
```

## Supported Types

- `line`: 단일 라인
- `multi-line`: 다중 라인
- `area`: 영역 채우기

## Implementation

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Design config 로드
import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    SERIES_COLORS, COLORS
)


def create_line_chart(
    data_path: str,
    title: str,
    x_field: str,
    y_fields: list[str],
    design: str = "four-pillars",
    output_path: str = "outputs/charts",
    **options
) -> dict:
    """
    라인 차트 생성

    Args:
        data_path: 데이터 파일 경로 (csv/json)
        title: 차트 제목
        x_field: X축 필드명
        y_fields: Y축 필드명(들)
        design: 디자인 템플릿
        output_path: 저장 경로
        **options: 추가 옵션 (fill, points, smooth 등)
    """

    # 1. 데이터 로드
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_json(data_path)

    # 2. Figure 생성
    chart_type = 'line' if len(y_fields) == 1 else 'multi-line'
    fig, ax = create_figure(chart_type)

    # 3. 플롯
    x_data = df[x_field]

    for i, y_field in enumerate(y_fields):
        color = SERIES_COLORS[i % len(SERIES_COLORS)]

        ax.plot(
            x_data,
            df[y_field],
            color=color,
            linewidth=options.get('linewidth', 2.5),
            label=y_field
        )

        # 영역 채우기
        if options.get('fill', False):
            ax.fill_between(
                x_data,
                df[y_field],
                alpha=0.1,
                color=color
            )

    # 4. Y축 라벨
    if options.get('ylabel'):
        ax.set_ylabel(options['ylabel'])

    # 5. 스타일 적용
    apply_style(fig, ax, chart_type)

    # 6. 저장
    filename = title.lower().replace(' ', '_')
    png_path, svg_path = save_chart(fig, filename, output_path)

    plt.close(fig)

    return {
        "success": True,
        "data": {
            "files": {
                "png": png_path,
                "svg": svg_path
            },
            "metadata": {
                "type": chart_type,
                "design": design,
                "dataPoints": len(df)
            }
        }
    }
```

## Example Usage

### 단일 라인
```python
result = create_line_chart(
    data_path="outputs/data/eth_tvl.csv",
    title="Ethereum TVL",
    x_field="date",
    y_fields=["tvl"],
    fill=True
)
```

### 다중 라인
```python
result = create_line_chart(
    data_path="outputs/data/chains_tvl.csv",
    title="Chain TVL Comparison",
    x_field="date",
    y_fields=["ethereum", "arbitrum", "optimism"],
    ylabel="TVL (USD)"
)
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| fill | bool | False | 영역 채우기 |
| linewidth | float | 2.5 | 라인 두께 |
| ylabel | string | None | Y축 라벨 |
| smooth | bool | True | 곡선 처리 (tension) |
