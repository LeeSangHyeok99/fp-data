# Data Validator

차트에 사용할 핵심 수치는 독립적인 소스 두 개 이상으로 교차 검증한다.

1. 원본과 비교 소스를 같은 기간, 단위, 시간대로 정규화한다.
2. `.claude/config/settings.json`의 지표별 허용 오차를 적용한다.
3. 비교값, 차이, 출처, 수집 시각을 `outputs/validation/`에 기록한다.
4. 통과 비율이 95% 이상이면 `VALIDATED`, 60% 이상이면 `PARTIAL`, 그 외는
   `FAILED`로 판정한다.
5. 비교 가능한 독립 소스가 두 개 미만이면 자동으로 `FAILED` 처리한다.

`PARTIAL`은 경고와 함께 진행할 수 있지만 `FAILED`는 사용자 확인 전 차트
생성을 중단한다.
