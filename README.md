# fp-data

차트 생성·검증 에이전트와 유형별로 정리한 차트, 인포그래픽을 보관하는 저장소입니다.

| 경로 | 내용 |
|---|---|
| `.claude/agents/chart.agent.md` | 차트 생성 컨트롤러 |
| `.claude/agents/validator.agent.md` | 데이터 2중 소스 교차 검증 컨트롤러 |
| `.claude/skills/assemble-infographic/` | 일반 차트 SVG를 1920×1080 인포그래픽으로 조립 |
| `.claude/skills/` | 차트, 데이터, 디자인, 출력 스킬 |
| `.claude/config/` | 경로와 데이터 소스 설정 |
| `outputs/charts/<type>/` | 라인, 바, 누적, 파이 등 유형별 차트 |
| `outputs/infographics/<type>/` | 유형별 인포그래픽 |
| `assets/font/` | 렌더링용 폰트 |

데이터셋과 뉴스레터 전용 구성, 주차별 차트는 포함하지 않습니다.

## 실행 환경

`.venv` 자체는 저장소에 넣지 않고 의존성 파일로 재생성합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

인포그래픽 PNG 렌더링에는 `rsvg-convert` (`librsvg`)가 필요합니다.
macOS에서는 `brew install librsvg`로 설치할 수 있습니다.
