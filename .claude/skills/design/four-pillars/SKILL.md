---
name: design-four-pillars
description: Four Pillars 스타일의 차트 디자인을 적용합니다. 다크 테마, matplotlib 기반 PNG/SVG 출력.
user-invocable: true
allowed-tools: Read, Write, Bash
argument-hint: [chart_file]
---

# Four Pillars Design Template

Four Pillars Research 스타일의 다크 테마 차트 디자인입니다.

## 리소스 파일

```
design-four-pillars/
├── SKILL.md      # 이 문서
├── colors.json   # 색상 정의 (JSON)
└── config.py     # matplotlib 설정 (Python)
```

## 색상 팔레트

### 기본
| 용도 | 색상 | HEX |
|-----|------|-----|
| 배경 | transparent | 투명 |
| 텍스트 | ██ | `#d1d4dc` |
| 보조 텍스트 | ██ | `#787b86` |
| 그리드 | ██ | `#787b86` (alpha 0.5) |

### 시리즈 색상
```python
SERIES_COLORS = [
    '#5470c6',  # 블루
    '#91cc75',  # 그린
    '#fac858',  # 옐로우
    '#ee6666',  # 레드
    '#73c0de',  # 라이트 블루
    '#3ba272',  # 틸
    '#fc8452',  # 오렌지
    '#9a60b4',  # 퍼플
    '#ea7ccc',  # 핑크
]
```

### 증감 표시
| 용도 | 색상 | HEX |
|-----|------|-----|
| 상승/긍정 | ██ | `#26a69a` |
| 하락/부정 | ██ | `#ef5350` |

## 스타일 규칙

### 폰트
```yaml
font_family: SUIT Bold
font_path: assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf
fallback: Arial Bold
weight: bold  # 모든 텍스트
```

### 축 설정
```yaml
y_label:
  fontsize: 20pt
  fontweight: bold
  padding: 20
  color: "#787b86"

y_tick:
  fontsize: 14pt
  fontweight: bold
  padding: 15
  tick_length: 0
  color: "#787b86"

x_tick:
  fontsize: 12pt
  fontweight: bold
  padding: 10
  rotation: 45deg
  alignment: right
  tick_length: 6
  tick_width: 1
  color: "#787b86"

spines: hidden  # 모든 축 선 숨김
```

### 그리드
```yaml
color: "#787b86"
alpha: 0.5
style: dashed
dashes: [3.7, 1.6]  # (dash, gap)
linewidth: 1.0
axis: y  # y축만
```

### 차트 크기
| 항목 | 값 |
|------|-----|
| 기본 크기 | 1600 x 700 px |
| DPI | 150 |
| figsize | 10.67 x 4.67 inch |

### 출력
```yaml
dpi: 150
formats: [PNG, SVG]
layout: tight_layout
```

## 사용법

### Python (matplotlib)

```python
import sys
sys.path.append('.claude/skills/design-four-pillars')
from config import create_figure, apply_style, save_chart, SERIES_COLORS

# 1. Figure 생성
fig, ax = create_figure('line')  # 'line', 'bar', 'stacked' 등

# 2. 데이터 플롯
ax.plot(x_data, y_data, color=SERIES_COLORS[0], linewidth=2)
ax.set_ylabel('Value')

# 3. 스타일 적용
apply_style(fig, ax, 'line')

# 4. 저장 (PNG + SVG)
png_path, svg_path = save_chart(fig, 'my_chart')
print(f"저장 완료: {png_path}")
```

### 색상 직접 사용

```python
from config import COLORS, SERIES_COLORS, POSITIVE_COLOR, NEGATIVE_COLOR

# 배경색
ax.set_facecolor(COLORS['background'])

# 텍스트
ax.set_title('Title', color=COLORS['text'])

# 시리즈 색상
for i, series in enumerate(data):
    ax.plot(series, color=SERIES_COLORS[i % len(SERIES_COLORS)])

# 증감 표시
color = POSITIVE_COLOR if value > 0 else NEGATIVE_COLOR
```

## 차트별 예시

### 라인 차트
```python
fig, ax = create_figure('line')
ax.plot(dates, values, color=SERIES_COLORS[0], linewidth=2.5)
ax.fill_between(dates, values, alpha=0.1, color=SERIES_COLORS[0])
apply_style(fig, ax, 'line')
save_chart(fig, 'tvl_trend')
```

### 스택 영역 차트
```python
fig, ax = create_figure('stacked')
ax.stackplot(dates, data1, data2, data3,
             colors=SERIES_COLORS[:3],
             labels=['A', 'B', 'C'])
ax.legend(loc='upper left', facecolor=COLORS['background'],
          edgecolor='none', labelcolor=COLORS['text'])
apply_style(fig, ax, 'stacked')
save_chart(fig, 'market_share')
```

### 바 차트
```python
fig, ax = create_figure('bar')
bars = ax.bar(categories, values, color=SERIES_COLORS[0])
apply_style(fig, ax, 'bar')
save_chart(fig, 'comparison')
```

## 출력 위치

```
outputs/charts/
├── {name}.png    # 150 DPI PNG
└── {name}.svg    # 벡터 SVG
```
