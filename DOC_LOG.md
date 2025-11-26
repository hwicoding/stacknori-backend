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
- **Date**: 2025-11-26
- **Author**: @hwicoding
- **Branch / Ref**: main
- **Related Issue / Ticket**: N/A

### 1. 작업 요약
- Alembic 초기화 및 `alembic/env.py` 커스터마이징(환경변수 기반 URL, metadata 로딩, Callout 활용)
- `UserModel` 정의, `UserRepository`가 실제 Session 기반 CRUD 수행하도록 구현
- 최초 마이그레이션 `create users table` 작성 및 `ALEMBIC_DATABASE_URL=postgresql+psycopg2://... alembic upgrade head`로 검증
- Notion API 버전 요구사항 갱신(`2025-09-03`), 워크플로우 재실행으로 동기화 확인
- `docs/AUTH_REQUIREMENTS.md`에 Auth 엔드포인트/유즈케이스/토큰 전략/테스트 계획 문서화
- Auth 서비스/라우터 구현: `app/usecases/auth.py`, `core/dependencies.py`, `/api/auth/*` 엔드포인트에서 회원가입·로그인·리프레시·/me 제공
- 스키마(`app/schemas`) 및 보안 유틸 확장(Access/Refresh 토큰/만료 설정), `example.env`에 Refresh 만료 분 추가
- **Auth 테스트 스위트 작성**: `tests/` 디렉토리 구조 생성, `conftest.py`에 SQLite in-memory DB 픽스처 및 FastAPI TestClient 설정
- **단위 테스트**: `test_auth_service.py`에서 `AuthService`의 회원가입/인증/토큰 발급/리프레시/현재 사용자 조회 시나리오 검증 (성공/실패 케이스 포함)
- **통합 테스트**: `test_auth_routes.py`에서 `/api/v1/auth/*` 엔드포인트의 HTTP 요청/응답 검증 (회원가입/로그인/리프레시/me 엔드포인트)
- `requirements.txt`에 `pytest`, `pytest-asyncio`, `pytest-cov`, `aiosqlite` 추가

> [!TIP] 데이터 계층을 실제 DB 스키마와 연결했으므로 이후 유스케이스/서비스에서 바로 Repository를 주입해 사용할 수 있음.
> [!TIP] 테스트는 SQLite in-memory DB를 사용하여 실제 PostgreSQL 없이도 빠르게 실행 가능하며, 각 테스트마다 독립적인 세션을 보장함.

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | Alembic CLI 실행 시 `ModuleNotFoundError: fastapi` |
| 원인 분석 | 호스트 Python 환경에 프로젝트 requirements 미설치 상태에서 `app/__init__` import 시 FastAPI 요구 |
| 선택한 해결책 | `pip install -r requirements.txt`로 로컬에도 동일 버전 의존성 설치, Alembic env import 성공 |
| 영향 범위/추가 조치 | 로컬 CLI에서 마이그레이션 수행 가능, README에 Alembic 사용법과 호스트 URL 지정 예시 추가 |
| 이슈 | Notion API 400: `missing_version` |
| 원인 분석 | 헤더에 `2023-08-02`를 사용했으나 Notion이 최신 버전(`2025-09-03`)만 허용 |
| 선택한 해결책 | `scripts/notion_sync.py`의 `NOTION_VERSION` 상수를 `2025-09-03`으로 교체 |
| 영향 범위/추가 조치 | 워크플로우 재실행 시 Notion 페이지 정상 생성, 향후 호환성 이슈 발생 시 버전 리스트 확인 필요 |
| 이슈 | Auth 요구사항이 문서화되지 않아 구현 범위 모호 |
| 원인 분석 | 엔드포인트/토큰 정책/테스트 계획을 구두로만 공유 |
| 선택한 해결책 | `docs/AUTH_REQUIREMENTS.md`로 목표/엔드포인트/토큰 전략/유즈케이스/테스트 전략 명시 |
| 영향 범위/추가 조치 | 유즈케이스/라우터 개발 시 기준선 확보, 변경 시 문서·DOC_LOG 동기화 필요 |
| 이슈 | DOC_LOG 자동 초기화 커밋과 로컬 커밋이 충돌 |
| 원인 분석 | Actions가 DOC_LOG를 초기화한 직후 동일 파일을 로컬에서 수정하여 push |
| 선택한 해결책 | `git pull --rebase origin main`으로 Actions 커밋을 반영하고 DOC_LOG를 수동 병합 후 push |
| 영향 범위/추가 조치 | 이후 DOC_LOG 커밋 시 rebase 루틴 준수, 충돌 시 즉시 해결 |
| 이슈 | 테스트 픽스처에서 FastAPI 의존성 오버라이드 실패 |
| 원인 분석 | `conftest.py`에서 `app.dependency_overrides.get`을 잘못된 방식으로 오버라이드 시도 |
| 선택한 해결책 | `from app.core.database import get_db`로 실제 의존성 함수를 import하고 `app.dependency_overrides[get_db]`로 정확히 오버라이드 |
| 영향 범위/추가 조치 | 테스트 클라이언트가 테스트 DB 세션을 정상적으로 사용, 각 테스트마다 독립적인 트랜잭션 보장 |

### 3. 다음 액션
- [ ] Alembic 자동화(도커 entrypoint 혹은 GH Actions) 설계
- [x] Auth 유즈케이스 단위 테스트 및 API 통합 테스트 작성
- [ ] 초기 Admin/Seed 전략 및 사용자 권한(Role) 정의
- [ ] CI/CD 파이프라인에 테스트 실행 단계 추가 (GitHub Actions)
