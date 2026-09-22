# Agent Communication Protocol

에이전트 간 통신 규약을 정의합니다.

## 핵심 원칙

> 에이전트는 다른 에이전트를 **직접 호출하지 않는다**. 공유 스킬 + 파일시스템을 통해 소통한다.

## 통신 방식

### 1. 파일시스템 기반 교환

에이전트 간 데이터는 `outputs/` 디렉토리의 파일을 통해 전달된다.

```
[Agent A] → outputs/{type}/{file} → [Agent B]
```

| 경로 | 용도 | 생산자 | 소비자 |
|------|------|--------|--------|
| `outputs/data/` | 원본/가공 데이터 | Crawler | Chart, Validator |
| `outputs/charts/` | 차트 이미지 + 메타데이터 | Chart | Output |
| `outputs/validation/` | 검증 결과 | Validator | Chart |

### 2. 공유 스킬 호출

에이전트는 자신의 `skills` 목록에 선언된 스킬만 사용할 수 있다.

```yaml
# chart.agent.md
skills:
  - core/_base      # 공통 규칙
  - core/_types     # 타입 정의
  - chart/*         # 차트 생성
  - design/*        # 디자인 설정
  - data/*          # 데이터 처리
  - output/*        # 출력
```

## 호출 방향

```
사용자 요청
    ↓
Chart Agent (컨트롤러)
    ├── data/crawler    → outputs/data/
    ├── data/validator  → outputs/validation/
    ├── chart/{type}    → 차트 렌더링
    ├── design/{style}  → 스타일 적용
    └── output/*        → outputs/charts/
```

### 허용된 호출 관계

| 호출자 | 피호출 스킬 | 설명 |
|--------|-------------|------|
| Chart Agent | data/crawler | 데이터 수집 |
| Chart Agent | data/parser | 데이터 파싱 |
| Chart Agent | data/validator | 데이터 검증 |
| Chart Agent | chart/* | 차트 렌더링 |
| Chart Agent | design/* | 스타일 로드 |
| Validator Agent | data/validator | 검증 실행 |
| Validator Agent | data/crawler | 교차 검증 데이터 수집 |

### 금지된 호출

- Agent → Agent 직접 호출 금지
- Skill → Agent 역방향 호출 금지
- Agent의 skills 목록에 없는 스킬 호출 금지

## Chart → Validator 호출 시퀀스

차트 생성 시 데이터 검증이 필요한 경우의 시퀀스:

```
Chart Agent
    │
    ├─[1] data/crawler.fetch()
    │     └── 원본 데이터 수집 → outputs/data/{name}_raw.json
    │
    ├─[2] data/parser.parse()
    │     └── 데이터 가공 → outputs/data/{name}_processed.json
    │
    ├─[3] data/validator.validate()
    │     ├── 교차 소스 수집 (data/crawler 재호출)
    │     ├── 비교 검증
    │     └── 결과 저장 → outputs/validation/{name}_validated.json
    │
    ├─[4] 검증 결과 판정
    │     ├── VALIDATED → [5]로 진행
    │     ├── PARTIAL → 경고 출력 후 [5]로 진행
    │     └── FAILED → 사용자 확인 요청
    │
    ├─[5] chart/{type} 렌더링
    │     └── design/{style} 스타일 적용
    │
    └─[6] output 저장
          ├── outputs/charts/{topic}/{name}.png
          ├── outputs/charts/{topic}/{name}.svg
          └── outputs/charts/{topic}/{name}.md
```

## 데이터 교환 형식

### 스킬 간 데이터 전달

스킬은 `_types.md`에 정의된 타입을 사용하여 데이터를 교환한다.

```python
# 입력: ChartRequest (사용자 → Chart Agent)
# 중간: RawData, ParsedData, ValidationResult (스킬 간)
# 출력: ChartResponse (Chart Agent → 사용자)
```

### 파일 기반 전달 규칙

1. 파일명은 `_base.md`의 네이밍 컨벤션을 따른다: `{subject}_{type}.{ext}`
2. JSON 파일은 UTF-8 인코딩, indent=2
3. 중간 결과물도 반드시 파일로 저장 (디버깅/재현성)

## 에러 전파 규칙

### 에러 발생 시 행동

1. **스킬 내부 에러**: `_base.md`의 에러 코드를 사용하여 실패 응답 반환
2. **에이전트 수준 에러**: 로그 기록 후 사용자에게 에러 메시지 출력
3. **복구 불가 에러**: 파이프라인 즉시 중단, 부분 결과물 보존

### 에러 전파 체인

```
스킬 에러 발생
    ↓
에러 응답 { success: false, error: { code, message } }
    ↓
호출한 에이전트가 에러 코드 확인
    ↓
├── 재시도 가능 (RATE_LIMIT_ERROR, TIMEOUT_ERROR)
│   └── 대기 후 재시도 (최대 3회)
│
├── 대체 경로 가능 (SOURCE_UNAVAILABLE)
│   └── 다른 소스로 재시도
│
└── 복구 불가 (VALIDATION_ERROR, RENDER_ERROR)
    └── 사용자에게 에러 보고
```

### 재시도 정책

| 에러 코드 | 재시도 | 최대 횟수 | 대기 시간 |
|-----------|--------|-----------|-----------|
| `RATE_LIMIT_ERROR` | O | 3 | Retry-After 헤더 또는 60s |
| `TIMEOUT_ERROR` | O | 2 | 5s |
| `SOURCE_UNAVAILABLE` | O (대체 소스) | 1 | 0s |
| `EXTERNAL_ERROR` | O | 2 | 3s |
| `VALIDATION_ERROR` | X | - | - |
| `RENDER_ERROR` | X | - | - |
