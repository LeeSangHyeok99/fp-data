---
name: data
description: 차트용 데이터 수집, 파싱, 교차 검증 서비스
user-invocable: false
allowed-tools: Read, Write, Bash, WebFetch
depends:
  - core/_base
  - core/_types
---

# Data Service

데이터 작업은 수집, 파싱, 검증의 세 단계로 분리한다.

| Step | File | Output |
|---|---|---|
| Collect | `crawler.md` | `outputs/data/*_raw.json` |
| Parse | `parser.md` | `outputs/data/*_processed.csv` or `.json` |
| Validate | `validator.md` | `outputs/validation/*_validated.json` |

기존 입력은 `outputs/data/`에서 읽고 원본을 수정하지 않는다. 외부 데이터를 가져올 때는
`.claude/config/sources.json`의 엔드포인트와 제한을 우선 사용한다.
