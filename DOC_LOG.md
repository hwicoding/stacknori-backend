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
- **Related Issue / Ticket**: Frontend API integration request

### 1. 작업 요약
- 로드맵/자료/진도 도메인 테이블 설계 및 Alembic 마이그레이션 (`roadmaps`, `materials`, `user_progress`, `material_scraps`)
- Domain/Infrastructure 계층 확장: 엔티티, Repository, Usecase, Schema, Router 추가
- 신규 API 구현
  - `GET /api/v1/roadmaps`: 분야별 계층 구조 + 사용자 완료 상태
  - `POST /api/v1/progress/{item_id}/complete`, `GET /api/v1/progress`
  - `GET /api/v1/materials` + 필터/페이지네이션, `POST|DELETE /api/v1/materials/{id}/scrap`
- JWT 토큰에 `iat/jti` 추가로 재발급 시 토큰 구분, API prefix `/api/v1`로 정비
- README에 API 개요 및 시드 스크립트 사용법 반영, requirements에 테스트용 의존성(python-multipart, greenlet, bcrypt) 추가
- `scripts/seed_content.py`로 로드맵/자료 기본 데이터 자동 입력 지원
- pytest 전체 통과(21 tests), CI에서 sqlite 호환성 확보(JSONB→JSON, .env Permission 대응)

> [!TIP] 프론트에서 요구한 5가지 API 스펙이 `/api/v1/*` 형태로 완성되었으며, 사용자별 완료/스크랩 상태까지 포함한 응답을 반환함.

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | 테스트 환경에서 `.env` 접근 권한 부족으로 Settings 초기화 실패 |
| 원인 분석 | macOS 보안 정책상 `.env` 파일 읽기 제한 |
| 선택한 해결책 | `get_settings()`에서 `PermissionError` 발생 시 `_env_file=None`로 재시도, 테스트 픽스처에서도 `_env_file=None` 지정 |
| 영향 범위/추가 조치 | CI/pytest에서 환경 변수 기반으로 동작, 프로덕션에는 영향 없음 |
| 이슈 | SQLite에서 `JSONB` 타입 미지원 |
| 원인 분석 | 테스트 DB가 SQLite라 Postgres 전용 타입 사용 불가 |
| 선택한 해결책 | 모델/마이그레이션 타입을 표준 `JSON`으로 변경 |
| 영향 범위/추가 조치 | Postgres에서도 JSON 컬럼 사용, 필요 시 추후 JSONB로 마이그레이션 가능 |
| 이슈 | Bcrypt backend 의존성 누락으로 해싱 실패 |
| 선택한 해결책 | requirements에 `bcrypt`, `python-multipart`, `greenlet` 추가 |
| 이슈 | `/api/v1/*` 요청이 404 응답 |
| 원인 분석 | `api_router`에 `/v1` prefix 미지정 |
| 선택한 해결책 | `APIRouter(prefix="/v1")`로 수정, 테스트 갱신 |
| 이슈 | Refresh 토큰 재발급 시 Access 토큰이 동일하게 생성 |
| 원인 분석 | JWT payload에 시간/랜덤 식별자가 없어 동일 시각 요청 시 동일 토큰 생성 |
| 선택한 해결책 | JWT payload에 `iat`, `jti` 추가하여 매번 고유 토큰 발급 |

### 3. 다음 액션
- [x] 로드맵/자료 콘텐츠 초기 데이터 시드 스크립트 작성 (직접 입력 or 관리 도구)
- [ ] 자료 완료(progress) 트래킹 범위 확장 여부 결정 (현재는 로드맵만 대상)
- [ ] CI에 새 API 통합 테스트 추가 및 문서화 자동화(Notion)에 API 변경 내역 연동



