# 데이터 시각화 에이전트 시스템 아키텍처

> 이 문서는 `.claude/` 아래 구성된 에이전트/스킬 시스템의 전체 아키텍처를 설명합니다.
> Notion 복붙에 최적화된 한국어 문서입니다.

---

## 1. 시스템 개요

온체인/금융 데이터를 수집, 검증, 시각화하는 자동화 파이프라인입니다. Claude Code의 에이전트/스킬 시스템 위에 구축되어 있으며, 자연어 명령(`/chart line`, `/validate` 등)으로 차트 생성부터 데이터 검증까지 처리합니다.

**핵심 특징**

- 데이터 교차 검증 필수 (최소 2개 소스)
- 두 가지 디자인 템플릿 (Four Pillars, HRC)
- 차트 생성 시 자동으로 제목 추천, 인사이트, 트위터 코멘트 생성
- 영문 + 한국어 번역 병기

---

## 2. 아키텍처

### 2-1. 디렉토리 구조

```
.claude/
├── README.md                # 시스템 진입점과 카탈로그
├── agents/                  # 에이전트 (컨트롤러)
│   ├── README.md            # 에이전트 등록 규칙
│   ├── chart.agent.md       # 차트 생성 파이프라인
│   └── validator.agent.md   # 데이터 검증
├── config/                  # 설정 파일
│   ├── settings.json        # 프로젝트 전역 설정
│   └── sources.json         # 데이터 소스 정의
├── docs/                    # 문서
│   └── ARCHITECTURE.md      # 이 파일
└── skills/                  # 스킬 (실행 모듈)
    ├── core/                # 공통 규칙
    │   ├── _base.md         # 에러 코드, 응답 형식, 로깅
    │   ├── _types.md        # 타입/인터페이스 정의
    │   └── _protocol.md     # 에이전트 간 통신 규약
    ├── chart/               # 차트 생성
    │   ├── SKILL.md         # 차트 서비스 인덱스
    │   ├── line.md          # 라인/영역 차트
    │   ├── bar.md           # 바 차트
    │   ├── stacked.md       # 스택 영역/바
    │   └── pie.md           # 파이/도넛
    ├── data/                # 데이터 처리
    │   ├── SKILL.md         # 데이터 서비스 인덱스
    │   ├── crawler.md       # API/웹 크롤링
    │   ├── parser.md        # CSV/JSON 파싱
    │   └── validator.md     # 교차 검증
    ├── design/              # 디자인 템플릿
    │   ├── SKILL.md         # 디자인 서비스 인덱스
    │   ├── four-pillars/    # Four Pillars 테마
    │   │   ├── SKILL.md
    │   │   ├── colors.json
    │   │   └── config.py
    │   └── hrc/             # HRC 테마
    │       ├── SKILL.md
    │       ├── colors.json
    │       └── config.py
    └── output/              # 출력
        └── SKILL.md         # PNG/SVG/HTML 저장
```

### 2-2. 의존성 그래프

```
         ┌──────────────────────────────────────┐
         │             사용자 요청                │
         │   /chart line ... / /validate ...     │
         └──────────┬───────────────┬────────────┘
                    │               │
            ┌───────▼──────┐ ┌─────▼──────────┐
            │ Chart Agent  │ │ Validator Agent │
            └───────┬──────┘ └─────┬──────────┘
                    │               │
    ┌───────────────┼───────────────┼────────────┐
    │           skills (공유 모듈)                 │
    │                                             │
    │  ┌─────────┐  ┌─────────┐  ┌────────────┐  │
    │  │  core/  │  │  data/  │  │  design/   │  │
    │  │ _base   │  │ crawler │  │ four-pills │  │
    │  │ _types  │  │ parser  │  │ hrc        │  │
    │  │ _proto  │  │ valid.  │  └────────────┘  │
    │  └─────────┘  └─────────┘                   │
    │                                             │
    │  ┌─────────┐  ┌──────────┐                  │
    │  │ chart/  │  │ output/  │                  │
    │  │ line    │  │ export   │                  │
    │  │ bar     │  └──────────┘                  │
    │  │ stacked │                                │
    │  │ pie     │                                │
    │  └─────────┘                                │
    └─────────────────────────────────────────────┘
                    │
            ┌───────▼──────┐
            │  파일시스템   │
            │ outputs/     │
            │  ├── data/   │
            │  ├── charts/ │
            │  └── valid./ │
            └──────────────┘
```

### 2-3. 데이터 흐름

```
[외부 API]                    [로컬 파일]
DefiLlama, CoinGecko, ...    CSV, JSON
        │                          │
        └──────────┬───────────────┘
                   │
            data/crawler
            (수집, Rate Limit)
                   │
                   ▼
            outputs/data/*_raw.json
                   │
            data/parser
            (정규화, 타입 변환)
                   │
                   ▼
            outputs/data/*.csv
                   │
         ┌─────────┴─────────┐
         │                   │
   data/validator        chart/{type}
   (2+ 소스 교차검증)     (시각화)
         │                   │
         ▼                   │
   outputs/validation/   design/{style}
         │              (스타일 적용)
         │                   │
         └─────────┬─────────┘
                   │
            output/export
            (PNG, SVG 저장)
                   │
                   ▼
            outputs/charts/{topic}/
            ├── {name}.png
            ├── {name}.svg
            └── {name}.md   ← 제목/인사이트/트위터
```

---

## 3. 에이전트 상세

### 3-1. Chart Agent

차트 생성의 전체 파이프라인을 관리하는 컨트롤러.

| 항목 | 값 |
|------|-----|
| 파일 | `agents/chart.agent.md` |
| 모델 | Opus |
| 도구 | Read, Write, Bash, Glob, WebFetch |

**라우팅**

| 명령 | 메서드 | 스킬 |
|------|--------|------|
| `/chart line` | createLineChart | chart/line |
| `/chart area` | createAreaChart | chart/line (fill=True) |
| `/chart bar` | createBarChart | chart/bar |
| `/chart stacked` | createStackedChart | chart/stacked |
| `/chart pie` | createPieChart | chart/pie |

**파이프라인 단계**

1. VALIDATE: 요청 파싱, 필수 필드 확인
2. LOAD DATA: 데이터 파일 미지정 시 `outputs/data/` 자동 스캔
3. DATA VALIDATION: 최소 2개 소스 교차 검증
4. LOAD DESIGN: `four-pillars` 또는 `hrc` 설정 로드
5. RENDER: `chart/{type}` 스킬로 차트 렌더링
6. OUTPUT: PNG/SVG 저장, .md 메타데이터 생성

### 3-2. Validator Agent

데이터 정확성 검증을 담당하는 컨트롤러.

| 항목 | 값 |
|------|-----|
| 파일 | `agents/validator.agent.md` |
| 모델 | Opus |
| 도구 | Read, Write, Bash, WebFetch, Glob, Grep |

**핵심 규칙**: 최소 2개 소스 검증 필수

**검증 판정 기준**

| 상태 | 조건 | 동작 |
|------|------|------|
| VALIDATED | 95%+ 일치 | 진행 |
| PARTIAL | 60%+ 일치 | 경고 출력 후 진행 |
| FAILED | 60% 미만 또는 소스 부족 | 사용자 확인 요청 |

---

## 4. 스킬 카탈로그

### 4-1. Core (공통)

| 스킬 | 설명 |
|------|------|
| `core/_base.md` | 입력 검증, 응답 형식, 에러 코드, 로깅 규칙, 파일 경로 규칙 |
| `core/_types.md` | ChartRequest, DataSource, ChartResponse, ValidationRequest 등 타입 정의 |
| `core/_protocol.md` | 에이전트 간 통신 규약 (직접 호출 금지, 파일시스템 기반 교환) |

### 4-2. Chart (차트 생성)

| 스킬 | 지원 타입 | 설명 |
|------|-----------|------|
| `chart/line.md` | line, multi-line, area (fill=True) | 라인/영역 차트 |
| `chart/bar.md` | bar, horizontal-bar | 바 차트 |
| `chart/stacked.md` | stacked-area, stacked-bar | 스택 차트 |
| `chart/pie.md` | pie, donut | 파이/도넛 차트 |

### 4-3. Data (데이터 처리)

| 스킬 | 설명 |
|------|------|
| `data/crawler.md` | API/웹 크롤링, Rate Limit 관리, 타임아웃/재시도 |
| `data/parser.md` | CSV/JSON 파싱, 스키마 적용, 날짜/숫자 정규화 |
| `data/validator.md` | 교차 검증, 허용 오차 비교, 신뢰도 산출 |

### 4-4. Design (디자인 템플릿)

| 템플릿 | 스타일 | 주요 용도 |
|--------|--------|-----------|
| `four-pillars` | 다크, 미니멀 | Four Pillars Research 리포트 |
| `hrc` | 다크, 네온 | HRC 트레이딩 대시보드 |

### 4-5. Output (출력)

| 포맷 | 확장자 | 용도 |
|------|--------|------|
| PNG | .png | 래스터 이미지 (투명 배경) |
| SVG | .svg | 벡터 그래픽 |
| HTML | .html | 인터랙티브 차트 |

---

## 5. 설정 파일

### 5-1. settings.json

프로젝트 전역 설정. 기본 디자인, 출력 포맷, 검증 허용 오차 등을 정의.

| 설정 | 값 | 설명 |
|------|-----|------|
| `defaults.design` | `four-pillars` | 기본 디자인 템플릿 |
| `defaults.output.formats` | `["png", "svg"]` | 기본 출력 포맷 |
| `defaults.output.dpi` | `150` | 기본 해상도 |
| `defaults.validation.minSources` | `2` | 최소 검증 소스 수 |

**검증 허용 오차**

| 데이터 유형 | 허용 오차 | 사유 |
|------------|-----------|------|
| TVL | 5% | 집계 시점 차이 |
| Price | 1% | 거래소별 차이 |
| Balance | 0% (정확) | 정확 일치 필수 |
| Volume | 5% | 집계 방식 차이 |
| APY | 10% | 계산 방식 차이 |

### 5-2. sources.json

외부 데이터 소스 정의. API 엔드포인트, Rate Limit, 검증 매핑.

**지원 소스**

| 소스 | Base URL | Rate Limit |
|------|----------|------------|
| DefiLlama | `api.llama.fi` | 100 req / 60s |
| CoinGecko | `api.coingecko.com/api/v3` | 30 req / 60s |
| Etherscan | `api.etherscan.io/api` | 5 req / 1s |
| Dune Analytics | `api.dune.com/api/v1` | API 키 필요 |

**검증 소스 매핑**

| 데이터 | Primary | Secondary |
|--------|---------|-----------|
| TVL | DefiLlama | CoinGecko, Protocol API |
| Price | CoinGecko | CoinMarketCap, Binance |
| Balance | Etherscan | Blockscout, Alchemy |

---

## 6. 차트 스타일 규칙

차트 이미지에 적용되는 공통 규칙입니다. 모든 디자인 템플릿에서 동일하게 적용됩니다.

### 6-1. 차트 포함하지 않는 것

| 항목 | 규칙 |
|------|------|
| 제목/부제목 | 차트에 포함 안 함 (외부에서 처리) |
| Source 표기 | 차트에 포함 안 함 |
| 범례 (legend) | 차트에 포함 안 함 |
| Y축 라벨 | 라벨 없음, 틱 값만 표시 |

### 6-2. Y축 규칙

| 규칙 | 상세 |
|------|------|
| 틱 최대 개수 | 5개 (`MaxNLocator(nbins=5)`) |
| 단위 통일 | $M이면 전부 $M, $B이면 전부 $B |
| 0값 단위 | `$0M` 또는 `$0B` (단위 포함) |
| 듀얼 축 | 좌/우 Y축 틱 개수 동일하게 정렬 |

### 6-3. 디자인 템플릿 비교

| 항목 | Four Pillars | HRC |
|------|-------------|-----|
| 배경 | transparent | transparent |
| 내부 배경 | `#141414` | `#0a3a34` |
| 텍스트 | `#d1d4dc` | `#ffffff` |
| 보조 텍스트 | `#787b86` | `#747474` |
| 그리드 | `#787b86` (점선, alpha 0.5) | `#1a5c52` (실선) |
| Y축 틱 크기 | 14pt | 18pt |
| X축 틱 크기 | 12pt | 16pt |
| 시리즈 색상 1 | `#5470c6` (블루) | `#00d4ff` (네온 시안) |
| 시리즈 색상 수 | 9개 | 6개 |
| 차트 크기 | 1600x700 px | 1600x700 px |
| DPI | 150 | 150 |

### 6-4. 텍스트 작성 규칙

- emdash/dash를 구분자로 사용 금지. 쉼표, 마침표, 괄호 사용
- 모든 텍스트에 영문 + 한국어 번역 병기
- 한줄 인사이트는 최대 20단어 이내 (영문 기준)
- 차트 제목은 한국어 번역 필수

---

## 7. 사용법 가이드

### 7-1. 차트 생성

```bash
# 기본 라인 차트
/chart line outputs/data/tvl.csv --title "TVL Trend"

# HRC 디자인 적용
/chart bar outputs/data/protocols.json --horizontal --design hrc

# 영역 차트
/chart area outputs/data/tvl.csv --title "TVL Area"

# 스택 차트
/chart stacked outputs/data/share.csv --title "Market Share"

# 파이/도넛
/chart pie outputs/data/distribution.json --donut
```

### 7-2. 데이터 검증

```bash
# 데이터 검증
/validate outputs/data/aave_tvl.json

# 사용 가능한 소스 조회
/validate sources
```

### 7-3. 디자인 적용

```bash
# 디자인 템플릿 적용 (차트 파일에)
/design-hrc outputs/charts/my_chart.png
```

### 7-4. 차트 생성 후 출력물

차트가 생성되면 다음 파일들이 자동으로 만들어집니다:

```
outputs/charts/{topic}/
├── {name}.png         # 래스터 이미지
├── {name}.svg         # 벡터 이미지
└── {name}.md          # 메타데이터
```

`.md` 파일에 포함되는 내용:
1. 차트 제목 추천 (영문 + 한국어, 3~5개)
2. 범례 정보 (시리즈명, 색상 코드, 대표 값)
3. 한줄 인사이트 (영문 + 한국어)
4. 트위터 코멘트 (영문 + 한국어, 3줄)
5. 검증 결과 (VALIDATED / PARTIAL / FAILED)

---

## 8. 에이전트 간 통신 프로토콜

### 8-1. 핵심 원칙

에이전트는 다른 에이전트를 직접 호출하지 않습니다. **공유 스킬 + 파일시스템**을 통해 소통합니다.

### 8-2. 통신 경로

| 경로 | 용도 | 생산자 | 소비자 |
|------|------|--------|--------|
| `outputs/data/` | 원본/가공 데이터 | Crawler | Chart, Validator |
| `outputs/charts/` | 차트 이미지 + 메타데이터 | Chart | Output |
| `outputs/validation/` | 검증 결과 | Validator | Chart |

### 8-3. 에러 전파

| 에러 코드 | 재시도 | 최대 횟수 | 대기 시간 |
|-----------|--------|-----------|-----------|
| RATE_LIMIT_ERROR | O | 3회 | Retry-After 또는 60s |
| TIMEOUT_ERROR | O | 2회 | 5s |
| SOURCE_UNAVAILABLE | O (대체 소스) | 1회 | 즉시 |
| EXTERNAL_ERROR | O | 2회 | 3s |
| VALIDATION_ERROR | X | - | - |
| RENDER_ERROR | X | - | - |

---

## 9. 에러 코드

| 코드 | 설명 | 발생 시점 |
|------|------|-----------|
| `VALIDATION_ERROR` | 입력 검증 실패 | 요청 파싱 단계 |
| `DATA_NOT_FOUND` | 데이터 없음 | 데이터 로드 단계 |
| `PARSE_ERROR` | 파싱 실패 | 데이터 파싱 단계 |
| `RENDER_ERROR` | 렌더링 실패 | 차트 생성 단계 |
| `OUTPUT_ERROR` | 출력 저장 실패 | 파일 저장 단계 |
| `EXTERNAL_ERROR` | 외부 API 실패 | API 호출 단계 |
| `RATE_LIMIT_ERROR` | API 요청 한도 초과 (429) | API 호출 단계 |
| `SOURCE_UNAVAILABLE` | 데이터 소스 접근 불가 | 데이터 수집 단계 |
| `TIMEOUT_ERROR` | 요청 시간 초과 | API 호출 단계 |

---

## 10. 알려진 제한사항

| 항목 | 상세 |
|------|------|
| area.md 미존재 | 별도 area.md 없음. `line.md`에서 `fill=True` 옵션으로 처리 |
| scatter 미지원 | scatter 차트 스킬 미구현 (사용 사례 없음) |
| settings.json 폰트 불일치 | settings.json에는 Pretendard로 선언되어 있으나, 실제 config.py에서는 SUIT 사용. config.py가 실제 적용됨 |
| COLORS['background'] 불일치 | colors.json의 background는 `transparent`, config.py의 background는 배경색 값. 의도적 설계 (JSON은 최종 출력용, config.py는 작업 중 미리보기용) |
| API 키 관리 | Etherscan, Dune 등 API 키가 필요한 소스는 별도 환경변수 설정 필요 |
| 인터랙티브 차트 | HTML 포맷 출력은 Chart.js 기반이며, matplotlib 스타일과 완벽히 일치하지 않음 |

---

## 부록: 타입 요약

### ChartRequest (주요 필드)

```
type:    line | multi-line | area | stacked-area | bar | horizontal-bar
         | stacked-bar | pie | donut
title:   string (필수)
data:    { type: csv|json|url|api, path: string, schema?: DataSchema }
design:  four-pillars | hrc (기본: four-pillars)
output:  { formats: [png, svg], dpi: 150, path: outputs/charts/ }
```

### ValidationRequest (주요 필드)

```
dataFile:    검증할 데이터 파일 경로
sources:     최소 2개 소스 배열 [{ name, type, endpoint, mapping? }]
tolerance:   필드별 허용 오차 (%) { tvl: 5, price: 1, ... }
```

### ChartResponse

```
success:     boolean
data:        { files: { png, svg }, metadata: { type, design, dataPoints } }
error:       { code: ERROR_CODE, message: string }
```
