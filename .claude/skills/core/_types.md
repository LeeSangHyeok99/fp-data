# Types & Interfaces

스킬 간 데이터 교환을 위한 타입 정의입니다.

---

## ChartRequest

차트 생성 요청

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `type` | ChartType | Y | - | 차트 종류 |
| `title` | string | Y | - | 차트 제목 |
| `subtitle` | string | N | null | 부제목 |
| `data` | DataSource | Y | - | 데이터 소스 |
| `design` | DesignType | N | "four-pillars" | 디자인 템플릿 |
| `output` | OutputConfig | N | default | 출력 설정 |
| `options` | ChartOptions | N | {} | 차트별 옵션 |

```typescript
interface ChartRequest {
  type: ChartType;
  title: string;
  subtitle?: string;
  data: DataSource;
  design?: DesignType;
  output?: OutputConfig;
  options?: ChartOptions;
}
```

---

## ChartType

```typescript
type ChartType =
  | "line"           // 라인 차트
  | "multi-line"     // 다중 라인
  | "area"           // 영역 차트
  | "stacked-area"   // 스택 영역
  | "bar"            // 수직 바
  | "horizontal-bar" // 수평 바
  | "stacked-bar"    // 스택 바
  | "pie"            // 파이
  | "donut"          // 도넛
  | "scatter";       // 스캐터
```

---

## DataSource

데이터 입력 소스

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | SourceType | Y | 소스 타입 |
| `path` | string | Y | 파일 경로 또는 URL |
| `schema` | DataSchema | N | 데이터 스키마 |
| `options` | object | N | 파싱 옵션 |

```typescript
interface DataSource {
  type: "csv" | "json" | "url" | "api";
  path: string;
  schema?: DataSchema;
  options?: {
    encoding?: string;      // default: "utf-8"
    delimiter?: string;     // CSV: default ","
    headers?: boolean;      // CSV: default true
    dateFormat?: string;    // 날짜 파싱 포맷
  };
}
```

---

## DataSchema

데이터 구조 정의

```typescript
interface DataSchema {
  x: {
    field: string;          // X축 필드명
    type: "date" | "category" | "number";
    format?: string;        // 날짜 포맷
  };
  y: {
    field: string | string[];  // Y축 필드명 (복수 가능)
    type: "number";
    label?: string;         // Y축 라벨
  };
  series?: {
    field: string;          // 시리즈 구분 필드
    colors?: string[];      // 시리즈별 색상
  };
}
```

---

## DesignType

```typescript
type DesignType = "four-pillars" | "hrc" | "custom";
```

---

## OutputConfig

출력 설정

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `formats` | string[] | N | ["png", "svg"] | 출력 포맷 |
| `dpi` | number | N | 150 | 해상도 |
| `path` | string | N | "outputs/charts/" | 저장 경로 |
| `filename` | string | N | auto | 파일명 |

```typescript
interface OutputConfig {
  formats?: ("png" | "svg" | "html")[];
  dpi?: number;
  path?: string;
  filename?: string;
}
```

---

## ChartOptions

차트별 추가 옵션

```typescript
interface ChartOptions {
  // 공통
  showLegend?: boolean;       // default: true
  legendPosition?: "top" | "bottom" | "left" | "right";
  showGrid?: boolean;         // default: true (y only)

  // 라인 차트
  lineWidth?: number;         // default: 2.5
  showPoints?: boolean;       // default: false
  fill?: boolean;             // default: false

  // 바 차트
  horizontal?: boolean;       // default: false
  stacked?: boolean;          // default: false
  barWidth?: number;          // default: 0.8

  // 파이/도넛
  showLabels?: boolean;       // default: true
  showPercent?: boolean;      // default: true
  innerRadius?: number;       // 도넛: default 0.6
}
```

---

## ChartResponse

차트 생성 결과

```typescript
interface ChartResponse {
  success: boolean;
  data?: {
    files: {
      png?: string;
      svg?: string;
      html?: string;
    };
    metadata: {
      type: ChartType;
      design: DesignType;
      dataPoints: number;
      generatedAt: string;
    };
  };
  error?: {
    code: string;
    message: string;
  };
}
```

---

## ValidationRequest

검증 요청

```typescript
interface ValidationRequest {
  dataFile: string;           // 검증할 데이터 파일
  sources: ValidationSource[];  // 최소 2개 필수
  tolerance?: {
    [field: string]: number;  // 필드별 허용 오차 (%)
  };
}

interface ValidationSource {
  name: string;               // 소스명 (defillama, coingecko 등)
  type: "api" | "url" | "file";
  endpoint: string;
  mapping?: {                 // 필드 매핑
    [originalField: string]: string;
  };
}
```

---

## ValidationResponse

```typescript
interface ValidationResponse {
  success: boolean;
  status: "VALIDATED" | "PARTIAL" | "FAILED";
  sourcesChecked: number;     // 확인된 소스 수
  sourcesRequired: number;    // 필요한 최소 소스 수 (2)
  confidence: number;         // 0.0 ~ 1.0
  checks: ValidationCheck[];
  summary: string;
}

interface ValidationCheck {
  field: string;
  source: string;
  original: any;
  validated: any;
  difference: string;         // "0.4%", "exact", etc.
  status: "pass" | "fail" | "warn";
}
```
