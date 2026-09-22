---
name: chart
description: 차트 생성 서비스. /chart로 호출.
user-invocable: true
allowed-tools: Read, Write, Bash
argument-hint: <type> [options]
depends:
  - core/_base
  - core/_types
  - design/*
  - output/*
---

# Chart Service

차트 생성을 담당하는 서비스입니다.

## Usage

```bash
/chart line outputs/data/tvl.csv --title "TVL Trend"
/chart bar outputs/data/protocols.json --horizontal
/chart stacked outputs/data/share.csv --design hrc
```

## Available Methods

| Method | File | Description |
|--------|------|-------------|
| line | line.md | 라인 차트 |
| multi-line | line.md | 다중 라인 |
| area | line.md (fill=True) | 영역 차트 |
| stacked | stacked.md | 스택 영역/바 |
| bar | bar.md | 바 차트 |
| pie | pie.md | 파이/도넛 |

## Style Rules

- **제목(title), 부제목(subtitle) 넣지 않음** - 차트 이미지에 텍스트 제목을 포함하지 않는다
- **Source 표기 넣지 않음** - 출처 텍스트를 차트에 포함하지 않는다
- **브랜드 컬러 사용** - 특정 프로토콜/서비스 데이터를 시각화할 때 해당 브랜드 컬러를 사용한다 (예: Pump.fun → #55d292)
- **범례(legend) 넣지 않음** - 차트 이미지에 범례를 포함하지 않는다
  - 원본 시리즈가 5개를 넘으면 표시 기간 전체 합계가 큰 상위 5개만 유지하고 나머지는 각 X값별로 합산한 `Others` 시리즈로 차트 자체를 다시 그린다. 범례만 합쳐서 원본 차트와 불일치하게 만들지 않는다
  - 최종 차트와 외부 범례는 최대 상위 5개와 `Others`, 총 6개 항목만 사용한다
- **Y축 라벨 넣지 않음** - Y축에 축 이름(label)을 표시하지 않는다. 틱 값(예: $20M)만 표시
- **차트 안 텍스트는 단어마다 첫 글자 대문자** - 주석, 카테고리 라벨, 축 틱 텍스트 등 차트 이미지에 그려지는 모든 영문 텍스트는 단어마다 첫 글자를 대문자로 쓴다. 단, 티커/브랜드/프로토콜명은 원래 표기를 그대로 유지한다
  - BAD: `unique depositors (left)`, `log scale`, `Dydx`, `Pump.fun`, `Stcusd`
  - GOOD: `Unique Depositors (Left)`, `Log Scale`, `dYdX`, `pump.fun`, `stcUSD`
  - 데이터(CSV/JSON)에서 온 라벨도 그리기 전에 적용한다. `.title()`을 그대로 쓰면 티커가 깨지므로 고유명사는 예외 처리
- **Y축 틱 최대 5개** - Y축 틱(눈금)은 최대 5개까지만 표시한다. `MaxNLocator(nbins=5)` 또는 수동 설정으로 제한
- **Y축 틱 값은 깔끔한 수로** - Y축 틱 값은 5 또는 10의 배수로 떨어지게 설정한다. 데이터 범위에 맞춰 간격을 $5M, $10M, $50M, $100M, $0.5B, $1B 등으로 설정. `$14B, $28B, $42B` 같은 어중간한 값을 쓰지 않는다
  - BAD: `$0B, $14B, $28B, $42B, $56B, $70B`
  - GOOD: `$0B, $10B, $20B, $30B, $40B, $50B`
  - GOOD: `$0, $50, $100, $150, $200, $250`
  - GOOD: `0%, 10%, 20%, 30%, 40%, 50%`
- **Y축 단위 통일** - 하나의 Y축 내에서 단위를 혼용하지 않는다. $M이면 전부 $M, $B이면 전부 $B. 값이 0일 때도 `$0M` 또는 `$0B`로 단위를 포함한다
  - BAD: `$0, $50M, $100M, $1.5B`
  - GOOD: `$0M, $100M, $200M, $300M, $400M`
  - GOOD: `$0.0B, $0.5B, $1.0B, $1.5B, $2.0B`
- **듀얼 Y축 틱 정렬** - 듀얼 축(twinx) 차트에서 좌/우 Y축의 틱 개수를 동일하게 맞춘다. 양쪽 모두 동일한 개수의 틱을 사용해 그리드 라인이 정확히 대응되도록 한다
- **X축 날짜 형식은 `Mon YYYY`** - 날짜 축에는 `strftime('%b %Y')` 형식을 사용한다 (예: `Mar 2024`, `Jan 2025`). `YY-MM-DD`, `YYYY-MM-DD`, 쉼표 포함 형식 등을 사용하지 않는다
- 차트는 순수 데이터 시각화만 담고, 제목/출처/범례는 차트 외부(문서, 캡션 등)에서 처리

## 텍스트 작성 규칙 (필수)

- **emdash(—), endash(–), dash(-), middle dot(·)를 구분자/연결자로 사용하지 않는다.** 문장을 이어 붙이거나 부연 설명할 때, 그리고 단어들을 나열할 때 emdash/endash/dash/middle dot 대신 쉼표(,), 마침표(.), 괄호(()), 또는 별도 문장으로 분리한다. Twitter, Context, Insight 등 모든 .md 텍스트에 동일하게 적용.
  - BAD: `Cash DEX surged to $2.6B — averaging $120M/day`
  - GOOD: `Cash DEX surged to $2.6B cumulative volume in 3 weeks, averaging $120M/day`
  - BAD: `the bet shifts to ecosystem — payments come along`
  - GOOD: `the bet shifts to ecosystem. Payments come along`
  - BAD: `카드사·VAN·PG 수수료`
  - GOOD: `카드사, VAN, PG 수수료`
  - BAD: `비용·정산 시간 측면`
  - GOOD: `비용과 정산 시간 측면`
- **"라벨: 설명" / "전제는 다음과 같음." / "단기 진단." 같은 라벨-인용 분리 패턴 금지.** 인용을 도입할 때 항상 동사("argues", "notes", "writes", "주장", "설명", "묘사", "평가")를 써서 완결 문장 안에 자연스럽게 녹여 쓴다. 콜론(:)이나 명사구+마침표로 인용을 떨어뜨려 두지 않는다.
  - BAD: `The setup: "Korea is already a cashless-dominant country."`
  - GOOD: `The report grounds the claim by noting that "Korea is already a cashless-dominant country."`
  - BAD: `100y의 예시. "스타벅스 코리아가 Case 4를 채택하면..."`
  - GOOD: `스타벅스 코리아가 핵심 예시로 등장하며, 이 체인이 Case 4를 채택하면 "수수료를 줄이면서..."`
  - BAD: `장기 경로 (섹션 1.3.3). "답은 생태계 구축..."`
  - GOOD: `섹션 1.3.3은 "답은 생태계 구축"이라고 주장하며, ...`
- **모든 텍스트 항목은 영문 + 한국어 번역을 함께 작성한다.** 차트 제목 추천, 한줄 인사이트, 트위터 코멘트 등 .md에 포함되는 모든 텍스트 콘텐츠에 한국어 번역을 병기한다.
- **한줄 인사이트는 간결하게** - 원라인 인사이트/코멘트는 1문장, 최대 15~20단어 이내로 작성한다. 숫자와 핵심 메시지만 담고, 불필요한 수식어를 제거한다.
  - BAD: `Moonwell and Millennium Club each hold ~19% of identified protocol veAERO, together controlling over a third of protocol-level Aerodrome governance power.`
  - GOOD: `Moonwell & Millennium Club hold 38% of protocol veAERO combined, dominating Aerodrome governance.`
- **차트 제목은 한국어 번역 필수** - 차트 제목 추천 시 영문 제목과 함께 반드시 한국어 번역을 병기한다.

## 차트 완료 후 .md 파일 (선택)

**기본 동작은 차트(PNG/SVG)만 생성하고 종료한다.** .md 파일은 명시적으로 요청한 경우에만 작성한다. 묻지 않는다.

### .md 작성 트리거 (아래 중 하나라도 해당 시 자동 작성)

- `--md` 플래그: `/chart [...] --md`
- 한국어 키워드: 사용자 메시지에 `md`, `문서`, `리서치`, `컨텍스트`, `트위터`, `뉴스레터` 중 하나 포함
- 영어 키워드: `with md`, `with doc`, `with context`, `with research`

### 사용 예시

```bash
# 차트만 (기본)
/chart [이미지]
/chart line outputs/data/tvl.csv

# 차트 + .md 문서
/chart [이미지] --md
/chart line outputs/data/tvl.csv --md
/chart [이미지] md 같이 만들어줘
/chart [이미지] 문서까지 작성해줘
```

플래그/키워드가 없으면 .md를 만들지 않고, 사용자에게 묻지도 않는다. 필요하면 사용자가 추후에 "md 만들어줘"라고 요청한다.

예: `outputs/charts/hyperliquid/stablecoin/hyperevm_stablecoin_supply.png` → `.md`

### .md 템플릿

아래 템플릿을 **반드시** 따른다. 섹션 순서, 헤딩 레벨, EN/KR 표기 방식을 그대로 유지한다.

````markdown
---
protocol: {protocol_name}
category: {semi_category}
chart_type: {stacked_area | line | bar | horizontal_bar | pie | donut}
data_date: {YYYY-MM-DD}
status: {VALIDATED | PARTIAL | FAILED}
source: {primary data source}
---

# {Chart File Name (확장자 제외)}

## Titles

차트가 **무엇을 보여주는지**를 단순 서술하는 제목. 인사이트나 수치를 넣지 않는다.

| EN | KR |
|----|-----|
| HyperEVM Stablecoin Supply | HyperEVM 스테이블코인 공급량 |
| HyperEVM Stablecoin Supply by Token | HyperEVM 토큰별 스테이블코인 공급량 |

## Insight

트위터/뉴스레터 상단에 들어가는 원라인 코멘트. 핵심 수치 + 메시지를 담는다.

> **EN** HyperEVM stablecoin supply hit $925M in 12 months, USDC now holds 63%.
>
> **KR** HyperEVM 스테이블코인 공급 12개월 만에 $925M 도달, USDC 63% 점유.

## Context

차트 숫자 뒤에 있는 **왜(Why)와 맥락(So What)**을 담는 섹션.
리서치 단계에서 수집한 정보를 바탕으로 작성한다.

**EN**
- USDC's surge coincides with Circle's native HyperEVM deployment announced in Dec '25, replacing the previous bridged USDC.e. Native issuance removes bridge risk and enables direct mint/redeem, attracting institutional capital.
- USDT0 growth stalled after LayerZero's OFT standard faced scrutiny over centralization risks in Nov '25. Meanwhile, USDH benefits from being Hyperliquid's native stablecoin with HLP yield integration.
- USDe's decline mirrors Ethena's broader contraction as funding rates turned negative in Q1 '26, reducing sUSDe yield attractiveness.

**KR**
- USDC 급증은 2025년 12월 Circle의 HyperEVM 네이티브 배포 발표와 맞물린다. 기존 브릿지 USDC.e를 대체하며 브릿지 리스크 제거 + 직접 민트/리딤이 가능해져 기관 자본 유입.
- USDT0 성장 정체는 2025년 11월 LayerZero OFT 표준의 중앙화 리스크 논란과 시기가 겹친다. 반면 USDH는 Hyperliquid 네이티브 스테이블코인으로 HLP 수익률 연동 이점.
- USDe 하락은 Ethena의 전반적 수축을 반영. Q1 '26 펀딩레이트 마이너스 전환으로 sUSDe 수익률 매력도 감소.

## Legend

| Series | Color | Value | Share |
|--------|-------|-------|-------|
| USDC | `#2775ca` | $587M | 63.4% |
| USDT0 | `#26a17b` | $156M | 16.9% |
| USDH | `#50e3c2` | $96M | 10.4% |

## Key Stats

| Metric | Value |
|--------|-------|
| Total Supply | $925M |
| 7d Change | +$128M (+16.1%) |
| 30d Change | +$565M (+157%) |

## Twitter

**EN**
1. HyperEVM stablecoin supply hit $925M. USDC holds 63% ($587M), up 157% in a month. But what's behind this growth?
2. The data tells the story: native USDC deployment via CCTP V2 (Dec 8) removed bridge risk and enabled direct deposits from 12+ chains. Within a week, +$360M flowed in, the single largest inflow event in HyperEVM history.
3. USDH quietly grew from $10M to $96M in 6 months, now 10.4% of supply. Supply cap just raised to $500M (19% utilized). Reserve revenue funds HYPE buybacks, creating a flywheel where stablecoin growth directly benefits the ecosystem.
4. With native issuance replacing bridges and multiple stablecoins competing for HyperEVM share, the next milestone is likely $1B+. The question is whether USDC's dominance holds as USDH scales its yield advantage.

**KR**
1. HyperEVM 스테이블코인 공급 $925M. USDC가 63%($587M)로 월간 157% 상승. 이 성장의 배경은?
2. 데이터가 말해줌. 12월 8일 CCTP V2를 통한 네이티브 USDC 배포로 브릿지 리스크 제거, 12개+ 체인에서 직접 입금 가능. 1주 만에 +$360M 유입, HyperEVM 역사상 최대 단일 유입 이벤트.
3. USDH는 조용히 $10M에서 $96M으로 6개월 만에 성장, 현재 공급의 10.4%. 공급 상한 $500M 상향(19% 사용 중). 준비금 수익이 HYPE 바이백에 쓰여 스테이블코인 성장이 생태계에 직접 기여하는 플라이휠.
4. 네이티브 발행이 브릿지를 대체하고 여러 스테이블코인이 HyperEVM 점유율 경쟁 중인 상황에서, 다음 마일스톤은 $1B+ 가능성. USDH가 수익률 우위를 확대하면 USDC 지배력이 유지될지가 관건.

## Breakdown

### 1번 근거
- [ASXN Hyperliquid Dashboard](https://hyperscreener.asxn.xyz/stablecoins) - USDC $587M, 총 $925M 수치 확인
- [Circle Announces Native USDC on HyperEVM](https://example.com) (Circle Blog, 2025-12-18) - 네이티브 배포 발표

**쉬운 설명:** HyperEVM이라는 블록체인 위에 스테이블코인(달러 연동 코인)이 1년 만에 $925M(약 1.2조원)이 쌓임. 그중 63%가 USDC인데, 한 달 만에 157% 늘었다는 건 두 달 전 대비 2.5배가 됐다는 뜻.

### 2번 근거
- ASXN 데이터 기반 계산: 12월 8일 CCTP V2 연결 → 12/15 +$159.8M → 12/16 +$200.2M = 이틀간 +$360M

**쉬운 설명:** 원래 USDC를 HyperEVM에 넣으려면 "브릿지"라는 중간 다리를 거쳐야 했음. 12월 8일에 Circle이 직접 연결(네이티브)해서 브릿지 없이 바로 넣을 수 있게 됨. 그러자 일주일 만에 $360M(약 4,700억원)이 한꺼번에 들어옴.

### 3번 근거
- USDH 출시일: 2025-09-22, 현재 $96M (ASXN 데이터)
- 공급 상한 $500M 상향: 2026-03-10

**쉬운 설명:** USDH는 Hyperliquid가 직접 만든 스테이블코인. 6개월 만에 $96M까지 커졌는데, 최대 발행 한도를 $500M까지 올려놓은 상태. 아직 19%만 썼으니 성장 여력이 있음. 준비금에서 나오는 수익으로 HYPE 토큰을 사서 소각하는 구조라, 스테이블코인이 늘면 생태계 전체에 이득.

### 4번 근거
- 1~3번 데이터에서 도출한 추론

**쉬운 설명:** 지금 USDC가 압도적이지만, USDH가 수익률(이자)을 더 주면 사람들이 USDC에서 USDH로 옮길 수 있음. 확정은 아니고 "관건"이라고 쓴 이유.

## Validation

`VALIDATED` (2 sources)

| Source | Result | Note |
|--------|--------|------|
| ASXN API | PASS | Playwright로 직접 추출 |
| DefiLlama | PASS | 총합 5% 이내 일치 |

## References

리서치 과정에서 참고한 기사, 트윗, 공식 발표 등. 날짜순 정렬.

- [Circle Announces Native USDC on HyperEVM](https://example.com) (Circle Blog, 2025-12-18)
- [Ethena Q1 2026: Funding Rate Challenges](https://example.com) (Ethena Forum, 2026-01-15)
- [ASXN Hyperliquid Dashboard](https://hyperscreener.asxn.xyz/stablecoins) (Data Source)

## Sources

- Data: ASXN API (api-hyperliquid.asxn.xyz)
- Dashboard: ASXN (hyperscreener.asxn.xyz/stablecoins)
- Script: `charts/hyperliquid_stablecoins_revenue.py`
````

### 템플릿 규칙

1. **Frontmatter 필수** - `protocol`, `category`, `chart_type`, `data_date`, `status`, `source` 6개 필드
2. **Titles는 단순 서술** - 차트가 무엇을 보여주는지만 적는다. 인사이트, 수치, 코멘트를 넣지 않는다. EN/KR 테이블로 나란히 배치
3. **Insight는 blockquote** - `>` 블록으로 시각적 강조. 트위터/뉴스레터 상단에 들어가는 원라인 코멘트. 핵심 수치 + 메시지. 최대 20단어(EN 기준). EN/KR 각 1줄
4. **Context 필수** - 숫자 뒤의 Why/So What. 리서치 기반. EN/KR 각 2~4개 불렛. 단순 수치 반복이 아닌 **원인, 배경, 시장 맥락**을 설명
5. **Legend 테이블 통일** - Series, Color(`backtick`으로 hex), Value, Share(선택) 4열
6. **Key Stats 테이블** - 핵심 수치 요약. 선택 섹션이지만 있으면 Legend 아래에 배치
7. **Twitter는 번호 리스트** - `1. 2. 3. 4.` 형식. EN/KR 블록을 `**EN**` / `**KR**` 볼드 라벨로 분리. `[Overview]`, `[Research]` 같은 태그를 쓰지 않는다. 흐름은 다음 순서를 따른다:
   - **1번: 현상 정의 + 인사이트** - 무슨 일이 일어났는지 핵심 수치와 함께 정의. 호기심을 유발하는 질문이나 관점 제시
   - **2번: 데이터 근거** - 데이터가 보여주는 팩트. 구체적 수치/날짜로 현상을 뒷받침
   - **3번: 현재 현황** - 지금 시장/프로토콜이 어떤 상태인지. Context 리서치 내용을 구체적으로 포함
   - **4번: 전망** - 앞으로 어떻게 될 것인지. 데이터 기반 추론, 관전 포인트 제시
   - 트위터 코멘트가 리서치 결과를 전달하는 주요 채널이므로, 구체적 날짜/수치/원인을 생략하지 않는다
   - **톤 규칙**:
     - 수사적 표현 금지: "진짜 이야기는 데이터에 있다", "숫자가 말해준다", "엔진", "게임체인저" 같은 오바 워딩 쓰지 않는다. 팩트만 담백하게
     - 확정적 단언 금지: "~할 것이다", "~는 확실하다" 대신 "~할 수 있다", "~가능성이 있다", "~여부가 관건" 등 유보적 표현 사용
     - 불필요한 브릿지 문장 금지: "But the real story is...", "Here's what matters" 같은 연결 문장은 쓰지 않는다. 바로 팩트로 들어간다
8. **Validation은 backtick 상태** - `` `VALIDATED` `` 형식 + 소스 테이블
9. **References 필수** - 리서치에서 참고한 기사/트윗/공식 발표. 날짜순. `[제목](URL) (소스, 날짜)` 형식
10. **Sources 마지막** - Data, Dashboard, Cross-validation, Script 경로 포함
11. **섹션 순서 고정** - Titles → Insight → Context → Legend → Key Stats → Twitter → Breakdown → Validation → References → Sources
12. **선택 섹션** - Key Stats, 주요 통계, 교육 자료 등은 Twitter 아래에 자유롭게 추가 가능하되, 필수 섹션 순서는 변경하지 않는다
13. **Breakdown 필수** - Twitter 코멘트 각 문장의 근거와 쉬운 설명을 제공하는 섹션. 트위터 번호(1~4번)에 대응하여 작성한다.
    - **근거**: 해당 문장의 출처 URL을 리스트로. 데이터에서 계산한 경우 계산 과정도 포함
    - **쉬운 설명**: 중학생도 이해할 수 있는 수준으로 부연. 비유 활용 가능. 전문 용어가 나오면 풀어서 설명
    - 이 섹션은 외부 공개용이 아닌 내부 참고용. 트위터 코멘트를 쓴 사람이 "왜 이렇게 썼는지" 근거를 바로 확인할 수 있게 하는 것이 목적

## 데이터 파일 자동 탐색 (필수)

데이터 파일 경로가 명시되지 않은 경우, **outputs/data/ 디렉토리를 스캔**하여 사용 가능한 파일 목록을 보여주고 선택하게 한다.

- `outputs/data/` 내 CSV, JSON 파일을 자동 탐색
- 파일명, 크기, 수정일을 리스트로 출력
- 사용자가 번호 또는 파일명으로 선택

## 입력 모드

차트 요청은 두 가지 모드로 들어온다. 모드에 따라 파이프라인이 다르다.

### 모드 A: 데이터 → 차트 (CSV/JSON 기반)
사용자가 데이터 파일을 지정하거나 `outputs/data/`에서 선택한다.

### 모드 B: 이미지 → 차트 (레퍼런스 재현)
사용자가 이미지를 첨부하고 "그려줘"라고 한다. 가장 빈번한 패턴.

**이미지 재현 플로우:**
1. 이미지에서 차트 타입, 시리즈 수, 색상, 축 범위, 데이터 포인트를 읽는다
2. 데이터를 CSV로 추출해 `outputs/data/`에 저장한다
3. 검증 가능한 수치가 있으면 (평균선 라벨, 테이블 등) 추출한 데이터와 대조한다
4. four-pillars 스타일로 차트를 새로 그린다 (원본 레이아웃 참고하되 우리 디자인 적용)
5. 차트 코드를 `charts/`에, 출력을 `outputs/charts/{topic}/`에 저장한다

**이미지에서 데이터를 못 뽑을 때:**
- Agent(background)로 외부 소스 검색을 병행한다
- API(CoinGlass, DefiLlama, CME 등) 또는 Playwright 크롤링으로 실데이터를 확보한다
- 실데이터를 못 구하면 이미지에서 근사값을 추출하되, .md에 "이미지 추출" 명시

## Pipeline

```
Input (ChartRequest or Image)
    ↓
[0] 모드 판별
    ├─ 이미지 첨부 → 모드 B (이미지 재현)
    └─ 데이터/텍스트 → 모드 A (데이터 기반)
    ↓
[1] 데이터 확보
    ├─ 모드 A: CSV/JSON 로드 또는 outputs/data/ 스캔
    └─ 모드 B: 이미지에서 추출 + 외부 소스 병행 검색
    ↓
[2] Data validation (교차 검증)
    ├─ VALIDATED / PARTIAL → 진행
    └─ FAILED → 경고 출력 후 사용자 확인
    ↓
[3] 리서치 (Context 수집)          ← NEW
    ├─ Agent(background)로 WebSearch/WebFetch 병행
    ├─ 데이터 변동의 원인/배경 조사
    ├─ 관련 기사, 공식 발표, 트윗 수집
    └─ 결과를 .md의 Context + References에 반영
    ↓
[4] 차트 코드 작성 → charts/{topic}.py
    ↓
[5] 실행 → outputs/charts/{protocol}/{category}/ (png + svg)
    ↓
[6] .md 생성 (선택) → 사용자에게 작성 여부를 묻고, 요청 시에만 진행
    ↓
Output
```

### 리서치 절차 (Step 3)

차트 데이터의 **Why**와 **So What**을 찾아 .md의 Context 섹션에 반영한다. 단순 수치 요약이 아닌, 숫자 뒤의 원인과 시장 맥락을 제공하는 것이 목적이다.

1. **리서치 실행** - 차트 생성과 **병렬**로 Agent(background)를 띄워 리서치를 수행한다
   - WebSearch: 프로토콜명 + 키워드 (예: "Hyperliquid USDC native deployment", "Ethena funding rate Q1 2026")
   - WebFetch: 공식 블로그, 거버넌스 포럼, 주요 미디어 기사
   - 최근 1~3개월 내 관련 뉴스/발표에 집중
2. **조사 대상** - 아래 질문에 답할 수 있는 정보를 찾는다
   - 이 수치가 **왜** 올랐거나 내렸는가? (원인)
   - 어떤 **이벤트/발표/업데이트**가 영향을 줬는가? (트리거)
   - 같은 카테고리의 **경쟁 프로토콜/체인과 비교**하면 어떤 위치인가? (맥락)
   - 이 추세가 **지속될 것인가, 일시적인가?** (전망, 있을 경우만)
3. **Context 작성** - 리서치 결과를 EN/KR 각 2~4개 불렛으로 정리
   - 각 불렛은 **팩트 기반** (출처 명시 가능한 정보만)
   - 추측/의견은 "~로 분석된다", "~가 배경으로 지목된다" 식으로 톤 조절
   - 데이터에서 이미 보이는 수치를 반복하지 않는다 (Key Stats/Insight와 중복 방지)
   - **주제 일관성** - 차트가 보여주는 데이터의 직접적 원인/맥락만 포함한다
     - BAD: 스테이블코인 공급 차트에 "Circle이 HYPE 토큰을 매입" (간접 관련)
     - GOOD: 스테이블코인 공급 차트에 "12/8 HyperCore 통합으로 CCTP 입금 활성화" (직접 원인)
     - 해당 차트의 시리즈에 없는 프로토콜/토큰 이야기는 최소화
     - 한 불렛에 하나의 주제만 담는다. 서로 다른 토큰의 이야기를 한 불렛에 합치지 않는다
   - **불렛 길이** - 불렛당 2~3문장 이내. 긴 설명이 필요하면 불렛을 나눈다
   - **검증 필수** - 리서치에서 수집한 정보는 반드시 출처 URL이 있어야 한다. URL 없이 "~로 알려져 있다"식 서술 금지. 출처를 찾지 못한 정보는 Context에 포함하지 않는다
4. **References 수집** - 리서치에서 참고한 소스를 날짜순으로 정리
   - 형식: `[제목](URL) (소스명, YYYY-MM-DD)`
   - 최소 2개, 가능하면 3~5개
   - 공식 발표 > 미디어 기사 > 트윗 순으로 우선

### 데이터 검증 절차 (Step 2)

차트에 사용되는 데이터의 신뢰성을 확보하기 위해, 차트 생성 전에 **최소 2개 소스**로 교차 검증한다.

1. **소스 확보** - 사용된 데이터와 동일한 지표를 제공하는 외부 소스 2개 이상 확인. 소스는 데이터 특성에 맞게 유연하게 선택:
   - 범용: DefiLlama, CoinGecko, Etherscan, Dune Analytics
   - 프로토콜 전용: 공식 대시보드, stats 사이트 (예: usdhstats.com, app.hyperliquid.xyz 등)
   - 커뮤니티/서드파티: 각 프로토콜 생태계의 트래커, 익스플로러
2. **교차 비교** - `data/validator.md` 모듈 활용, 필드별 허용 오차 내 일치 여부 확인
3. **결과 판정**:
   - `VALIDATED` (95%+ 일치) → 차트 생성 진행
   - `PARTIAL` (60%+ 일치) → 불일치 항목 경고 출력 후 진행
   - `FAILED` (60% 미만 또는 소스 부족) → 사용자에게 확인 요청, 승인 시에만 진행
4. **검증 결과 출력** - 차트 완료 텍스트에 검증 상태 포함

## 비주얼 이펙트 (config.py에 정의)

`four-pillars/config.py`에 재사용 가능한 이펙트 함수가 있다. 차트 코드에서 직접 import해서 쓴다.

| 함수 | 용도 | 예시 |
|------|------|------|
| `gradient_rounded_bar()` | 그라데이션 + 라운드 탑 바 | Theo 월별 수익률 차트 |
| `area_glow()` | 라인 근처 글로우 에어리어 필 | Gold Futures OI 차트 |
| `endpoint_dot()` | 시리즈 끝점 마커 | 라인 차트 끝점 강조 |

```python
from config import gradient_rounded_bar, area_glow, endpoint_dot

# 그라데이션 라운드 바
gradient_rounded_bar(ax, x_center=0, width=0.17, height=11.77, color='#C9A84C')

# 에어리어 글로우 (라인 근처만 빛남)
area_glow(ax, dates, gold_values, color='#C9A84C')

# 끝점 도트
endpoint_dot(ax, dates.iloc[-1], gold_values.iloc[-1], color='#C9A84C')
```

## 출력 디렉토리 규칙 (필수)

차트 출력 경로는 **프로토콜/토픽(대분류) > 세미 카테고리(소분류)** 2단계 구조를 따른다.

```
outputs/charts/{protocol_or_topic}/{semi_category}/
```

**예시:**
```
outputs/charts/hyperliquid/stablecoin/    ← HyperEVM 스테이블코인
outputs/charts/hyperliquid/revenue/       ← Hyperliquid 수익
outputs/charts/hyperliquid/volume/        ← Hyperliquid 거래량
outputs/charts/hyperliquid/tvl/           ← Hyperliquid TVL
outputs/charts/hyperliquid/hip3/          ← HIP-3 관련
outputs/charts/hyperliquid/token/         ← HYPE 토큰 가격
outputs/charts/hyperliquid/metrics/       ← 빌더, 유저 메트릭
outputs/charts/hyperliquid/evm/           ← HyperEVM DEX 등
outputs/charts/sui/stablecoin/            ← Sui 스테이블코인
outputs/charts/morpho/token/              ← Morpho 토큰 언락
```

**규칙:**
- 프로토콜 루트(`outputs/charts/hyperliquid/`)에 직접 파일을 저장하지 않는다
- 반드시 세미 카테고리 하위 폴더를 만들어 그 안에 저장한다
- 세미 카테고리가 명확하지 않으면 `general/`을 사용한다
- .md 메타 파일도 같은 세미 카테고리 폴더에 저장한다
- 차트 코드(`charts/*.py`)는 기존과 동일하게 `charts/` 루트에 저장한다

## Common Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--title` | string | required | 차트 제목 |
| `--design` | string | four-pillars | 디자인 템플릿 |
| `--output` | string | outputs/charts/{topic}/ | 저장 경로 (프로토콜/토픽별 하위 폴더) |
| `--format` | string | png,svg | 출력 포맷 |

## Chart-specific Options

### Line/Area
- `--fill`: 영역 채우기
- `--points`: 포인트 표시
- `--smooth`: 곡선 처리

### Bar
- `--horizontal`: 수평 바
- `--stacked`: 스택 바

### Pie
- `--donut`: 도넛 차트
- `--labels`: 라벨 표시
