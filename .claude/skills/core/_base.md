# BaseService

모든 스킬이 상속받는 공통 규칙입니다.

## 입력 검증

```python
def validate_request(request: dict, schema: dict) -> ValidationResult:
    """
    1. 필수 파라미터 확인
    2. 타입 검증
    3. 범위/enum 검증
    """
    errors = []

    for field, rules in schema.items():
        if rules.get('required') and field not in request:
            errors.append(f"Missing required field: {field}")

        if field in request:
            if not isinstance(request[field], rules['type']):
                errors.append(f"Invalid type for {field}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

## 응답 형식

### 성공
```json
{
  "success": true,
  "data": {
    "result": "...",
    "metadata": {}
  },
  "timestamp": "ISO8601"
}
```

### 실패
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  },
  "timestamp": "ISO8601"
}
```

## 에러 코드

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | 입력 검증 실패 |
| `DATA_NOT_FOUND` | 데이터 없음 |
| `PARSE_ERROR` | 파싱 실패 |
| `RENDER_ERROR` | 렌더링 실패 |
| `OUTPUT_ERROR` | 출력 저장 실패 |
| `EXTERNAL_ERROR` | 외부 API 실패 |
| `RATE_LIMIT_ERROR` | API 요청 한도 초과 (429) |
| `SOURCE_UNAVAILABLE` | 데이터 소스 접근 불가 |
| `TIMEOUT_ERROR` | 요청 시간 초과 |

## 로깅 규칙

```
[ServiceName] START: {action} - {params}
[ServiceName] PROGRESS: {step} - {details}
[ServiceName] SUCCESS: {result_summary}
[ServiceName] ERROR: {error_code} - {message}
```

## 파일 경로 규칙

| 타입 | 경로 | 예시 |
|------|------|------|
| 소스 데이터 (원본 CSV/JSON) | `sources/` | `sources/hip3_daily_volume.csv` |
| 에이전트 가공 데이터 | `outputs/data/` | `outputs/data/tvl_processed.csv` |
| 차트 이미지 | `outputs/charts/{topic}/` | `outputs/charts/hyperliquid/volume/perp_volume.png` |
| 검증 결과 | `outputs/validation/` | `outputs/validation/tvl_validated.json` |

## 네이밍 컨벤션

```
{subject}_{type}_{timestamp?}.{ext}

예시:
- ethereum_tvl_line.png
- defi_protocols_bar.svg
- aave_tvl_validated.json
```
