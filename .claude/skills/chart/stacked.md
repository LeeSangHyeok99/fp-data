# Stacked Area Chart

스택 영역 차트 생성 모듈

## Signature

```python
def create_stacked_chart(request: ChartRequest) -> ChartResponse
```

## Supported Types

- `stacked-area`: 스택 영역
- `100%-stacked`: 100% 스택 (비율)

## Implementation

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    SERIES_COLORS, COLORS
)


def create_stacked_chart(
    data_path: str,
    title: str,
    x_field: str,
    stack_fields: list[str],
    design: str = "four-pillars",
    output_path: str = "outputs/charts",
    **options
) -> dict:
    """
    스택 영역 차트 생성

    Args:
        data_path: 데이터 파일 경로
        title: 차트 제목
        x_field: X축 필드명
        stack_fields: 스택할 필드명들
        **options: normalize (100% 스택), labels
    """

    # 1. 데이터 로드
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_json(data_path)

    # 2. Figure 생성
    fig, ax = create_figure('stacked')

    x_data = df[x_field]

    # 스택 데이터 준비
    stack_data = [df[field].values for field in stack_fields]

    # 100% 스택 (정규화)
    if options.get('normalize', False):
        totals = np.sum(stack_data, axis=0)
        stack_data = [data / totals * 100 for data in stack_data]

    # 3. 스택 플롯
    colors = [SERIES_COLORS[i % len(SERIES_COLORS)]
              for i in range(len(stack_fields))]

    ax.stackplot(
        x_data,
        *stack_data,
        labels=stack_fields,
        colors=colors,
        alpha=0.8
    )

    # 4. Y축 라벨
    if options.get('ylabel'):
        ax.set_ylabel(options['ylabel'])

    # 5. Y축 범위 (100% 스택일 때)
    if options.get('normalize', False):
        ax.set_ylim(0, 100)
        ax.set_ylabel('Share (%)')

    # 6. 스타일 적용
    apply_style(fig, ax, 'stacked')

    # 7. 저장
    filename = title.lower().replace(' ', '_')
    png_path, svg_path = save_chart(fig, filename, output_path)

    plt.close(fig)

    return {
        "success": True,
        "data": {
            "files": {"png": png_path, "svg": svg_path},
            "metadata": {
                "type": "stacked-area",
                "design": design,
                "dataPoints": len(df),
                "series": len(stack_fields)
            }
        }
    }
```

## Example Usage

### 기본 스택 영역
```python
result = create_stacked_chart(
    data_path="outputs/data/chain_tvl_history.csv",
    title="L2 TVL Over Time",
    x_field="date",
    stack_fields=["arbitrum", "optimism", "base", "zksync"],
    ylabel="TVL (USD)"
)
```

### 100% 스택 (점유율)
```python
result = create_stacked_chart(
    data_path="outputs/data/market_share.csv",
    title="DEX Market Share",
    x_field="date",
    stack_fields=["uniswap", "curve", "balancer", "other"],
    normalize=True
)
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| normalize | bool | False | 100% 스택 |
| ylabel | string | None | Y축 라벨 |
| legend_loc | string | upper left | 범례 위치 |
| alpha | float | 0.8 | 투명도 |

## Style Rules

### X축 여백 제거
시계열 stacked area / 100% stacked 차트에서는 X축 범위를 데이터에 딱 맞춘다. 좌우 여백 없이 차트가 y축에 붙어야 한다.
```python
ax.set_xlim(dates.min(), dates.max())
```
