# Chart And Validation Agents

`agents/chart.agent.md`가 차트 생성 흐름을, `agents/validator.agent.md`가
두 개 이상 소스의 교차 검증을 담당합니다. 세부 규칙은
`skills/chart`, `skills/data`, `skills/design`, `skills/output`에 나뉘어 있으며,
기본 입출력 경로는 `config/settings.json`에서 관리합니다.

`skills/assemble-infographic`는 생성된 차트 SVG 하나를 Four Pillars
1920×1080 템플릿에 넣어 SVG와 PNG를 생성합니다. 주간 뉴스레터
조립 스킬은 이 저장소의 범위가 아닙니다.
