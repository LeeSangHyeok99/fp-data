# Bar Chart

바 차트 생성 모듈

## Signature

```python
def create_bar_chart(request: ChartRequest) -> ChartResponse
```

## Supported Types

- `bar`: 수직 바
- `horizontal-bar`: 수평 바
- `stacked-bar`: 스택 바
- `grouped-bar`: 그룹 바

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


def create_bar_chart(
    data_path: str,
    title: str,
    category_field: str,
    value_fields: list[str],
    design: str = "four-pillars",
    output_path: str = "outputs/charts",
    **options
) -> dict:
    """
    바 차트 생성

    Args:
        data_path: 데이터 파일 경로
        title: 차트 제목
        category_field: 카테고리 필드명
        value_fields: 값 필드명(들)
        **options: horizontal, stacked, grouped
    """

    # 1. 데이터 로드
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_json(data_path)

    # 2. Figure 생성
    fig, ax = create_figure('bar')

    categories = df[category_field].tolist()
    x = np.arange(len(categories))
    width = options.get('bar_width', 0.75)

    horizontal = options.get('horizontal', False)
    stacked = options.get('stacked', False)

    # 3. 플롯
    if len(value_fields) == 1:
        # 단일 시리즈
        values = df[value_fields[0]].tolist()
        if horizontal:
            ax.barh(x, values, height=width, color=SERIES_COLORS[0])
        else:
            ax.bar(x, values, width=width, color=SERIES_COLORS[0])

    elif stacked:
        # 스택 바
        bottom = np.zeros(len(categories))
        for i, field in enumerate(value_fields):
            values = df[field].tolist()
            color = SERIES_COLORS[i % len(SERIES_COLORS)]

            if horizontal:
                ax.barh(x, values, height=width, left=bottom,
                       label=field, color=color)
            else:
                ax.bar(x, values, width=width, bottom=bottom,
                      label=field, color=color)
            bottom += np.array(values)

    else:
        # 그룹 바
        n_fields = len(value_fields)
        group_width = width / n_fields

        for i, field in enumerate(value_fields):
            values = df[field].tolist()
            offset = (i - n_fields/2 + 0.5) * group_width
            color = SERIES_COLORS[i % len(SERIES_COLORS)]

            if horizontal:
                ax.barh(x + offset, values, height=group_width * 0.9,
                       label=field, color=color)
            else:
                ax.bar(x + offset, values, width=group_width * 0.9,
                      label=field, color=color)

    # 4. 축 라벨
    if horizontal:
        ax.set_yticks(x)
        ax.set_yticklabels(categories)
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(categories)

    # 5. 스타일 적용
    apply_style(fig, ax, 'bar')

    # 6. 저장
    filename = title.lower().replace(' ', '_')
    png_path, svg_path = save_chart(fig, filename, output_path)

    plt.close(fig)

    return {
        "success": True,
        "data": {
            "files": {"png": png_path, "svg": svg_path},
            "metadata": {
                "type": "bar",
                "design": design,
                "dataPoints": len(df)
            }
        }
    }
```

## Example Usage

### 기본 바 차트
```python
result = create_bar_chart(
    data_path="outputs/data/protocols.json",
    title="Top DeFi Protocols by TVL",
    category_field="protocol",
    value_fields=["tvl"]
)
```

### 수평 바 차트
```python
result = create_bar_chart(
    data_path="outputs/data/chains.csv",
    title="Chain Comparison",
    category_field="chain",
    value_fields=["tvl"],
    horizontal=True
)
```

### 스택 바 차트
```python
result = create_bar_chart(
    data_path="outputs/data/defi_categories.csv",
    title="DeFi by Category",
    category_field="protocol",
    value_fields=["lending", "dex", "derivatives"],
    stacked=True
)
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| horizontal | bool | False | 수평 바 |
| stacked | bool | False | 스택 바 |
| bar_width | float | 0.75 | 바 너비 |
| show_values | bool | False | 값 표시 |
