## Stacknori DOC Log

> 이 파일은 작업 중간 로그를 기록한 뒤 push하면 Notion DB로 자동 전송됩니다.  
> 작성 → `git add DOC_LOG.md` → `git commit` → `git push` → Actions 완료 후 파일이 초기화되며, 아래 템플릿이 다시 채워집니다.

### 작성 루틴
1. **작업 전**: 현재 목표/이슈를 `0. 메타` 영역에 간단히 적고 브랜치/참조 티켓을 명시합니다.
2. **작업 중**: 문제 해결 과정과 의사결정을 `2. Troubleshooting & Decisions` 표에 적습니다.
3. **작업 후**: 완료한 내용과 다음 액션을 각각 `1. 작업 요약`, `3. 다음 액션` 섹션에 정리합니다.
4. **Push**: 커밋 메시지를 간결하게 남기고 push하면 Notion에 Markdown 구조 그대로 저장됩니다.

---

### 0. 메타
- **Date**: 2025-11-27
- **Author**: @hwicoding
- **Branch / Ref**: main
- **Related Issue / Ticket**: DeprecationWarning 해결 및 API 문서화 개선

### 1. 작업 요약
- DeprecationWarning 해결: `datetime.utcnow()` → `datetime.now(timezone.utc)` 변경 (`app/infrastructure/repositories/progress_repository.py`)
- Pydantic Config 마이그레이션: `class Config:` → `model_config = ConfigDict(...)` 변경 (6개 엔티티 파일 + `app/core/config.py`)
- API 문서화 개선: OpenAPI 스키마에 상세 설명 및 예제 응답 추가 (`app/main.py`의 `custom_openapi` 함수)
- 경고 수 감소: 48개 → 40개 (Pydantic DeprecationWarning 대부분 해결)

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | Python 3.12에서 `datetime.utcnow()` DeprecationWarning 발생 |
| 원인 분석 | Python 3.12부터 `datetime.utcnow()`가 deprecated, timezone-aware datetime 사용 권장 |
| 선택한 해결책 | `datetime.now(timezone.utc)`로 변경하여 timezone-aware datetime 사용 |
| 영향 범위/추가 조치 | `completed_at` 필드에 timezone 정보 포함, DB와의 호환성 유지 |
| 이슈 | Pydantic v2에서 `class Config:` 사용 시 DeprecationWarning 발생 |
| 원인 분석 | Pydantic v2는 `ConfigDict`를 사용하도록 권장, `BaseSettings`는 `SettingsConfigDict` 사용 |
| 선택한 해결책 | 모든 엔티티와 Settings 클래스에 `model_config = ConfigDict(...)` 또는 `SettingsConfigDict(...)` 적용 |
| 영향 범위/추가 조치 | Pydantic v3 대비 호환성 확보, 경고 메시지 감소로 로그 가독성 향상 |
| 이슈 | OpenAPI 문서에 예제 응답이 없어 API 사용자 이해도 저하 |
| 원인 분석 | FastAPI 기본 OpenAPI 스키마에는 예제가 포함되지 않음 |
| 선택한 해결책 | `custom_openapi` 함수로 OpenAPI 스키마 커스터마이징, 주요 응답 스키마에 예제 추가 |
| 영향 범위/추가 조치 | `/docs`에서 예제 확인 가능, API 사용자 온보딩 시간 단축 |

### 3. 다음 액션
- [ ] Usecase/Repository 레벨 단위 테스트 추가 (현재 54-79% 커버리지)
- [ ] 남은 DeprecationWarning 해결 (httpx, jose 등 외부 라이브러리 경고)
