---
protocol: macro
category: distressed_debt
chart_type: bar
data_date: 2026-05-11
status: PARTIAL
source: Growth Market Reports (Distressed Debt Market segment)
---

# global_distressed_debt_absolute_opportunity

## Titles

| EN | KR |
|----|-----|
| Global Distressed Debt Absolute Opportunity (2025–2033) | 글로벌 부실채권 절대 기회 규모 (2025–2033) |
| Annual Distressed Debt Opportunity Set by Year | 연도별 절대 투자 기회 집합 |

## Insight

> **EN** Annual distressed debt opportunity set grows from $15.6B in 2025 to $29.3B by 2033 at 8.2% CAGR.
>
> **KR** 연간 부실채권 절대 기회는 2025년 $15.6B에서 2033년 $29.3B로 성장 (CAGR 8.2%).

## Context

**EN**
- The series tracks the actively deployable opportunity slice rather than total outstanding distressed paper, sized at $15.6B in 2025 and compounding at the same 8.2% CAGR as the broader market headline.
- Dry powder coverage looks tight against this curve. Distressed debt funds held roughly $57B of dry powder as of September 2024, equivalent to about three years of the annual opportunity even before accounting for new fund formation.
- The 2028 maturity wall sits inside the projection window. With around $674B in bonds and leveraged loans maturing that year, a single refi cycle can compress multiple years of opportunity into a short window, making the smooth CAGR line a baseline rather than a path.

**KR**
- 본 시리즈는 전체 부실채권 잔액이 아닌 연간 실제 투자 가능한 기회 슬라이스를 추적. 2025년 $15.6B에서 시장 전체와 동일한 8.2% CAGR로 복리 성장.
- 드라이파우더 대비로는 빠듯한 곡선. 2024년 9월 기준 부실채권 펀드 드라이파우더 약 $57B는 신규 펀드 결성 없이도 연간 기회의 약 3년치에 해당.
- 2028년 만기 절벽이 본 전망 구간 안에 있음. 해당 연도 약 $674B의 채권/레버리지론 만기 도래로, 단 한 번의 리파이낸싱 사이클이 수년치 기회를 짧은 기간에 압축시킬 수 있어, 매끈한 CAGR 선은 어디까지나 베이스라인.

## Legend

| Series | Color | 2025 | 2033 |
|--------|-------|------|------|
| Absolute Opportunity | `#fac858` | $15.6B | $29.3B |

## Key Stats

| Metric | Value |
|--------|-------|
| 2025 Opportunity | $15.6B |
| 2033 Forecast | $29.3B |
| CAGR (2025–2033) | 8.2% |
| Dry Powder (Sep 2024) | ~$57B |

## Twitter

**EN**
1. The investable distressed debt opportunity is sized at $15.6B in 2025, scaling to $29.3B by 2033 on an 8.2% CAGR. The figure measures the deployable slice, not the total outstanding distressed paper.
2. Dry powder already covers multiple years of this curve. Distressed funds held about $57B of dry powder as of September 2024, roughly three years of annual opportunity at the current pace, before new fundraising lands.
3. The 2028 maturity wall sits inside the forecast window. Around $674B of bonds and leveraged loans mature that year, and refi failures could compress several years of opportunity into a single vintage rather than spreading evenly along the CAGR line.
4. The takeaway is structural rather than directional. The path is unlikely to be smooth, and timing the entry around maturity events may matter more than the cumulative size of the opportunity set.

**KR**
1. 투자 가능한 부실채권 기회는 2025년 $15.6B, 2033년 $29.3B로 8.2% CAGR. 전체 잔액이 아닌 실제 집행 가능한 슬라이스 측정치.
2. 드라이파우더는 이미 수년치 커버. 2024년 9월 기준 부실채권 펀드 약 $57B 드라이파우더는 현재 페이스 기준 약 3년치 기회. 추가 펀드 결성분은 별도.
3. 2028년 만기 절벽이 본 전망 구간 안. 해당 연도 약 $674B 만기 도래로, 리파이낸싱 실패 시 수년치 기회가 한 빈티지로 압축될 가능성. CAGR 선처럼 균등 분포가 아닐 수 있음.
4. 시사점은 방향성보다 구조적 측면. 곡선이 매끈하게 그려질 가능성은 낮고, 누적 규모보다는 만기 이벤트 주변의 진입 타이밍이 더 중요한 변수가 될 수 있음.

## Breakdown

### 1번 근거
- [Growth Market Reports - Distressed Debt Market 2033](https://growthmarketreports.com/report/distressed-debt-market) - 8.2% CAGR 일치
- CSV `outputs/data/distressed_debt_absolute_opportunity.csv` - $15.6B (2025) → $29.3B (2033) 계산값

**쉬운 설명:** 시장 전체 규모(잔액)와 별개로, 한 해에 실제로 사고팔 수 있는 부실채권 거래량은 더 작음. 그 부분이 2025년 $15.6B(약 21조원)에서 2033년 $29.3B(약 40조원)로 성장. 시장 전체와 같은 8.2%씩 늘어남.

### 2번 근거
- [Alternative Credit Investor - Market volatility creates distressed debt opportunity](https://alternativecreditinvestor.com/2025/05/19/market-volatility-creates-distressed-debt-opportunity/) - $57B 드라이파우더 수치
- $57B / $15.6B ≈ 3.65년치 (계산)

**쉬운 설명:** 살 사람들이 가진 현금이 이미 너무 많음. 매년 사고팔 수 있는 부실채권보다 살 돈이 3배 많다는 뜻. 그래서 부실채권이 시장에 나오면 경쟁이 치열해 가격이 비싸질 수 있음.

### 3번 근거
- [Morningstar - 2025 US Distressed Outlook](https://www.morningstar.com/markets/2025-us-distressed-outlook-market-strength-boost-defaults-opportunity-set) - 2028년 $674B 만기 통계

**쉬운 설명:** 차트는 매년 8.2%씩 균등하게 증가하는 직선처럼 보이지만, 실제로는 2028년에 빚이 한꺼번에 만기 도래해서 그 해에만 부실채권이 몰릴 가능성. 즉, "이 차트는 평균값일 뿐, 실제로는 들쭉날쭉할 수 있음"이라는 경고.

### 4번 근거
- 1~3번 데이터에서 도출한 추론

**쉬운 설명:** 부실채권 투자자 입장에서는 "얼마나 큰가"보다 "언제 들어갈까"가 더 중요할 수 있다는 의견. 데이터 기반 추론이지 단정은 아님.

## Validation

`PARTIAL` (1 source + cross-check)

| Source | Result | Note |
|--------|--------|------|
| Growth Market Reports | PASS | 8.2% CAGR 일치 (시장 규모 헤드라인과 동일) |
| Base value (15.6B) source | UNVERIFIED | 정확한 세그먼트 출처 미확인. 잠정적으로 deployable opportunity로 해석 |

> **데이터 단위 주의** CSV 값(15.621, 29.344 등)은 단위가 **$B(billion)**. 차트 코드(`charts/global_distressed_debt_absolute_opportunity.py:44`)의 Y축 포맷터는 `$M`로 표기되어 있으나 이는 라벨 오기. 베이스 값 $15.6B(2025)의 출처/정의는 [[global-distressed-debt-market-size]] 헤드라인과 같은 8.2% CAGR이며, 별도 세그먼트 보고서로 추정.

## References

- [Growth Market Reports - Distressed Debt Market Research Report 2033](https://growthmarketreports.com/report/distressed-debt-market) (Market Research, 2025)
- [Morningstar - 2025 US Distressed Outlook](https://www.morningstar.com/markets/2025-us-distressed-outlook-market-strength-boost-defaults-opportunity-set) (Morningstar, 2025)
- [Alternative Credit Investor - Market volatility creates distressed debt opportunity](https://alternativecreditinvestor.com/2025/05/19/market-volatility-creates-distressed-debt-opportunity/) (Alternative Credit Investor, 2025-05-19)
- [RBC BlueBay - Distressed Debt: investor opportunities in 2025](https://www.rbcbluebay.com/globalassets/documents/distressed-debt-investor-opportunies-in-2025.pdf) (RBC BlueBay, 2025)

## Sources

- Data: Growth Market Reports (segment)
- Dashboard: growthmarketreports.com/report/distressed-debt-market
- Script: `charts/global_distressed_debt_absolute_opportunity.py`
