---
name: design-hrc
description: HRC 스타일의 차트 디자인을 적용합니다. 다크 테마의 프로페셔널한 디자인입니다.
user-invocable: true
allowed-tools: Read, Write
argument-hint: [chart_file]
---

# HRC Design Template

HRC(Hashed Research Center) 스타일의 다크 테마 프로페셔널 차트 디자인입니다.

## 리소스 경로

```yaml
font_path: /assets/font/SUIT/SUIT-ttf/
reference_images: /assets/img/
```

## 디자인 특징

- **다크 테마**: 어두운 배경으로 데이터 강조
- **네온 액센트**: 눈에 띄는 형광색 포인트
- **데이터 중심**: 숫자와 트렌드가 부각
- **크립토/금융**: 트레이딩 대시보드 스타일

## 컬러 팔레트

```yaml
# Background
background: "transparent"  # 투명 (인포그래픽 워터마크 호환)
surface: "#0a3a34"        # 카드 배경
surface_light: "#0f4d45"  # 호버/포커스
border: "#1a5c52"         # 보더

# Primary Colors
primary: "#00d4ff"        # 네온 시안
secondary: "#7c3aed"      # 일렉트릭 퍼플
success: "#10b981"        # 네온 그린
warning: "#f59e0b"        # 앰버
danger: "#ef4444"         # 레드

# Text
text_primary: "#ffffff"     # 화이트
text_secondary: "#747474"   # 축 라벨/보조 텍스트
text_muted: "#747474"       # 축 틱/뮤트 텍스트

# Chart Colors (시리즈)
chart_colors:
  - "#00d4ff"  # 네온 시안
  - "#7c3aed"  # 퍼플
  - "#10b981"  # 그린
  - "#f59e0b"  # 앰버
  - "#ec4899"  # 핑크
  - "#06b6d4"  # 틸

# Brand Colors (프로토콜별)
brand_colors:
  walrus: "#97F0E5"
```

## 차트 크기

| 항목 | 값 |
|------|-----|
| 기본 크기 | 1600 x 700 px |
| DPI | 150 |
| figsize | 10.67 x 4.67 inch |

## 스타일 규칙

### 타이포그래피
```css
/* 로컬 SUIT 폰트 사용 */
@font-face {
  font-family: 'SUIT';
  src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Regular.ttf') format('truetype');
  font-weight: 400;
}
@font-face {
  font-family: 'SUIT';
  src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Medium.ttf') format('truetype');
  font-weight: 500;
}
@font-face {
  font-family: 'SUIT';
  src: url('/assets/font/SUIT/SUIT-ttf/SUIT-SemiBold.ttf') format('truetype');
  font-weight: 600;
}
@font-face {
  font-family: 'SUIT';
  src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf') format('truetype');
  font-weight: 700;
}
@font-face {
  font-family: 'SUIT';
  src: url('/assets/font/SUIT/SUIT-ttf/SUIT-ExtraBold.ttf') format('truetype');
  font-weight: 800;
}

font-family: 'SUIT', 'Space Grotesk', monospace;
title: 28px, font-weight: 700, color: text_primary;
subtitle: 14px, font-weight: 400, color: text_secondary;
label: 11px, font-weight: 500, text-transform: uppercase;
value: 16px, font-weight: 600;
```

### 차트 스타일
```yaml
# 라인 차트
line:
  borderWidth: 2.5
  tension: 0.4
  pointRadius: 0
  pointHoverRadius: 6
  fill: true
  backgroundColor: "rgba(0, 212, 255, 0.1)"  # 그라데이션 영역

# 바 차트
bar:
  borderRadius: 2
  borderWidth: 0
  barPercentage: 0.6
  hoverBackgroundColor: "rgba(255, 255, 255, 0.2)"

# 파이/도넛
pie:
  cutout: "70%"
  borderWidth: 0
  spacing: 4
  hoverOffset: 8

# 공통
grid:
  color: "#787b86"
  alpha: 0.5
  lineStyle: "dashed (3.7, 1.6)"
  lineWidth: 1
  drawBorder: false
y_label:
  fontsize: 20pt
  fontweight: bold
y_tick:
  fontsize: 18pt
  fontweight: bold
  max_ticks: 6          # Y축 틱 5~6개로 제한 (MaxNLocator nbins)
x_tick:
  fontsize: 16pt
  fontweight: bold
  rotation: 45
  ha: right
  tick_length: 6
  tick_width: 1
  color: "#747474"
```

### 특수 효과
```yaml
# 글로우 효과 (CSS)
glow:
  text-shadow: "0 0 10px rgba(0, 212, 255, 0.5)"
  box-shadow: "0 0 20px rgba(0, 212, 255, 0.2)"

# 그라데이션 라인
gradient:
  type: "linear"
  start: "#00d4ff"
  end: "#7c3aed"
```

## Chart.js 설정 템플릿

```javascript
const hrcConfig = {
  options: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#a0aec0',
          usePointStyle: true,
          padding: 24,
          font: { family: 'Space Grotesk', size: 12 }
        }
      },
      tooltip: {
        backgroundColor: '#0f4d45',
        titleColor: '#ffffff',
        bodyColor: '#a0aec0',
        borderColor: '#1a5c52',
        borderWidth: 1,
        titleFont: { family: 'Space Grotesk', weight: 700 },
        bodyFont: { family: 'Space Grotesk' },
        padding: 16,
        cornerRadius: 4
      }
    },
    scales: {
      x: {
        grid: {
          color: '#1a5c52',
          drawBorder: false
        },
        ticks: {
          font: { family: 'Space Grotesk', size: 14 },
          color: '#747474',
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        grid: {
          color: '#1a5c52',
          drawBorder: false
        },
        ticks: {
          font: { family: 'Space Grotesk', size: 14 },
          color: '#747474'
        }
      }
    }
  }
};
```

## HTML 템플릿

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    @font-face {
      font-family: 'SUIT';
      src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Regular.ttf') format('truetype');
      font-weight: 400;
    }
    @font-face {
      font-family: 'SUIT';
      src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Medium.ttf') format('truetype');
      font-weight: 500;
    }
    @font-face {
      font-family: 'SUIT';
      src: url('/assets/font/SUIT/SUIT-ttf/SUIT-SemiBold.ttf') format('truetype');
      font-weight: 600;
    }
    @font-face {
      font-family: 'SUIT';
      src: url('/assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf') format('truetype');
      font-weight: 700;
    }
    @font-face {
      font-family: 'SUIT';
      src: url('/assets/font/SUIT/SUIT-ttf/SUIT-ExtraBold.ttf') format('truetype');
      font-weight: 800;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'SUIT', 'Space Grotesk', sans-serif;
      background: #042622;
      padding: 40px;
      min-height: 100vh;
    }
    .chart-container {
      max-width: 900px;
      margin: 0 auto;
      background: #0a3a34;
      border: 1px solid #1a5c52;
      border-radius: 8px;
      padding: 32px;
    }
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
    }
    .chart-title {
      font-size: 24px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 4px;
    }
    .chart-subtitle {
      font-size: 13px;
      color: #747474;
    }
    .chart-value {
      text-align: right;
    }
    .chart-value-main {
      font-size: 28px;
      font-weight: 700;
      color: #00d4ff;
      font-family: monospace;
    }
    .chart-value-change {
      font-size: 13px;
      color: #10b981;
    }
    .chart-value-change.negative {
      color: #ef4444;
    }
  </style>
</head>
<body>
  <div class="chart-container">
    <div class="chart-header">
      <div>
        <h1 class="chart-title">{{title}}</h1>
        <p class="chart-subtitle">{{subtitle}}</p>
      </div>
      <div class="chart-value">
        <div class="chart-value-main">{{main_value}}</div>
        <div class="chart-value-change {{change_class}}">{{change}}</div>
      </div>
    </div>
    <canvas id="chart"></canvas>
  </div>
  <script>
    // Chart configuration here
  </script>
</body>
</html>
```

## 적용 방법

1. 차트 데이터 준비
2. 위 컬러 팔레트와 스타일 적용
3. Chart.js 설정에 hrcConfig 병합
4. 그라데이션/글로우 효과 추가 (선택)
5. HTML 템플릿으로 출력

## 추가 기능

### 숫자 포맷팅
```javascript
// 큰 숫자 축약
function formatNumber(num) {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
}
```

### 애니메이션
```javascript
animation: {
  duration: 1000,
  easing: 'easeOutQuart'
}
```
