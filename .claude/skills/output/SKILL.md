---
name: output
description: 차트/데이터 출력 서비스
user-invocable: false
allowed-tools: Write, Bash
depends:
  - core/_base
---

# Output Service

차트와 데이터의 출력을 담당하는 서비스입니다.

## Supported Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| PNG | .png | 이미지 (래스터) |
| SVG | .svg | 벡터 그래픽 |
| HTML | .html | 인터랙티브 차트 |
| CSV | .csv | 데이터 테이블 |
| JSON | .json | 구조화된 데이터 |

## Implementation

```python
import matplotlib.pyplot as plt
from pathlib import Path


def export_chart(
    fig,
    filename: str,
    output_dir: str = "outputs/charts",
    formats: list = ["png", "svg"],
    dpi: int = 150,
    background: str = "#141414"
) -> dict:
    """
    차트를 다양한 포맷으로 저장

    Args:
        fig: matplotlib Figure 객체
        filename: 파일명 (확장자 제외)
        output_dir: 출력 디렉토리
        formats: 출력 포맷 리스트
        dpi: 해상도 (PNG용)
        background: 배경색
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved = {}

    for fmt in formats:
        filepath = output_path / f"{filename}.{fmt}"

        if fmt == "png":
            fig.savefig(
                filepath,
                dpi=dpi,
                facecolor=background,
                edgecolor='none',
                bbox_inches='tight',
                pad_inches=0.2
            )
        elif fmt == "svg":
            fig.savefig(
                filepath,
                format='svg',
                facecolor=background,
                edgecolor='none',
                bbox_inches='tight'
            )

        saved[fmt] = str(filepath)

    return saved


def export_data(
    data,
    filename: str,
    output_dir: str = "outputs/data",
    formats: list = ["csv", "json"]
) -> dict:
    """
    데이터를 다양한 포맷으로 저장

    Args:
        data: pandas DataFrame 또는 dict
        filename: 파일명 (확장자 제외)
        output_dir: 출력 디렉토리
        formats: 출력 포맷 리스트
    """
    import pandas as pd
    import json

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # DataFrame으로 변환
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data

    saved = {}

    for fmt in formats:
        filepath = output_path / f"{filename}.{fmt}"

        if fmt == "csv":
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif fmt == "json":
            df.to_json(filepath, orient='records', date_format='iso', indent=2)

        saved[fmt] = str(filepath)

    return saved
```

## Output Paths

```yaml
charts:
  base: outputs/charts/{topic}/
  structure:
    hyperliquid:
      volume: outputs/charts/hyperliquid/volume/
      revenue: outputs/charts/hyperliquid/revenue/
      metrics: outputs/charts/hyperliquid/metrics/
      tvl: outputs/charts/hyperliquid/tvl/
      evm: outputs/charts/hyperliquid/evm/
    hip3: outputs/charts/hip3/
    usdh: outputs/charts/usdh/
    walrus: outputs/charts/walrus/
    steth: outputs/charts/steth/
    defi: outputs/charts/defi/
    korean_etf: outputs/charts/korean_etf/
  naming: "{subject}_{type}.{ext}"
  example: "hyperliquid/volume/hyperliquid_perp_volume_monthly.png"

data:
  base: outputs/data/
  raw: "{subject}_raw.json"
  processed: "{subject}.csv"
  validated: outputs/validation/{subject}_validated.json
```

## Filename Convention

```python
def generate_filename(
    subject: str,
    chart_type: str = None,
    suffix: str = None
) -> str:
    """
    일관된 파일명 생성

    Examples:
        generate_filename("ethereum_tvl", "line") → "ethereum_tvl_line"
        generate_filename("aave", suffix="validated") → "aave_validated"
    """
    parts = [subject.lower().replace(' ', '_')]

    if chart_type:
        parts.append(chart_type)

    if suffix:
        parts.append(suffix)

    return "_".join(parts)
```
