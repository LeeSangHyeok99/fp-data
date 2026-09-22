---
name: design
description: 차트 디자인 템플릿 서비스
user-invocable: false
allowed-tools: Read
depends:
  - core/_base
---

# Design Service

차트 디자인 템플릿을 관리하는 서비스입니다.

## Available Templates

| Template | Style | Description |
|----------|-------|-------------|
| four-pillars | Dark, Minimal | Four Pillars Research 스타일 |
| hrc | Dark, Neon | HRC 대시보드 스타일 |

## Template Structure

```
design/
├── SKILL.md           # 이 파일 (index)
├── four-pillars/
│   ├── SKILL.md       # 사용 가이드
│   ├── config.py      # matplotlib 설정
│   └── colors.json    # 색상 정의
└── hrc/
    ├── SKILL.md       # 사용 가이드
    ├── config.py      # matplotlib 설정
    └── colors.json    # 색상 정의
```

## Common Interface

모든 디자인 템플릿은 동일한 인터페이스를 제공합니다:

### config.py

```python
# 필수 exports
from config import (
    COLORS,           # 색상 dict
    SERIES_COLORS,    # 시리즈 색상 list
    create_figure,    # Figure 생성 함수
    apply_style,      # 스타일 적용 함수
    save_chart,       # 저장 함수
)
```

### colors.json

```json
{
  "name": "template-name",
  "background": "#hex",
  "text": {
    "primary": "#hex",
    "secondary": "#hex"
  },
  "grid": {
    "color": "#hex",
    "alpha": 0.5
  },
  "chart_colors": {
    "series": ["#hex", ...],
    "positive": "#hex",
    "negative": "#hex"
  }
}
```

## Usage

```python
# 디자인 로드
import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart

# 또는 동적 로드
def load_design(name: str):
    import importlib.util
    config_path = f'.claude/skills/design/{name}/config.py'
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config
```
