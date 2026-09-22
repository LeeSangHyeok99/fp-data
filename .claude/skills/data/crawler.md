# Data Crawler

외부 API와 웹 소스에서 재현 가능한 원본 데이터를 수집한다.

1. `.claude/config/sources.json`에서 소스, 엔드포인트, 요청 제한을 확인한다.
2. API 키가 필요한 소스는 환경 변수만 사용하며 파일이나 로그에 키를 쓰지 않는다.
3. 타임아웃은 30초, 일시적 오류와 HTTP 429는 지수 백오프로 최대 3회 재시도한다.
4. 응답 본문은 가공 전에 `outputs/data/<name>_raw.json`으로 보존한다.
5. 요청 URL, 수집 시각, HTTP 상태, 출처명을 메타데이터에 기록한다.

접근할 수 없는 소스는 `SOURCE_UNAVAILABLE`, 제한 초과는
`RATE_LIMIT_ERROR`, 시간 초과는 `TIMEOUT_ERROR`로 반환한다.
