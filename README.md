# fp-data

차트 생성·검증 에이전트와 생성 결과, 차트 데이터만 보관하는 저장소입니다.

| 경로 | 내용 |
|---|---|
| `.claude/agents/chart.agent.md` | 차트 생성 컨트롤러 |
| `.claude/agents/validator.agent.md` | 데이터 2중 소스 교차 검증 컨트롤러 |
| `.claude/skills/` | 차트, 데이터, 디자인, 출력 스킬 |
| `.claude/config/` | 경로와 데이터 소스 설정 |
| `outputs/charts/` | 생성된 PNG, SVG 차트와 `by-type/` 유형별 복사본 |
| `outputs/data/` | 차트 생성에 사용한 CSV, JSON 데이터 |
| `assets/font/` | 렌더링용 폰트 |

뉴스레터 전용 에이전트, 스킬, 주차별 차트는 포함하지 않습니다.
