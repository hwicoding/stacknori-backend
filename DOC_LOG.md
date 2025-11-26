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

> [!TIP] 데이터 계층을 실제 DB 스키마와 연결했으므로 이후 유스케이스/서비스에서 바로 Repository를 주입해 사용할 수 있음.

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | Alembic CLI 실행 시 `ModuleNotFoundError: fastapi` |
| 원인 분석 | 호스트 Python 환경에 프로젝트 requirements 미설치 상태에서 `app/__init__` import 시 FastAPI 요구 |
| 선택한 해결책 | `pip install -r requirements.txt`로 로컬에도 동일 버전 의존성 설치, Alembic env import 성공 |
| 영향 범위/추가 조치 | 로컬 CLI에서 마이그레이션 수행 가능, README에 Alembic 사용법과 호스트 URL 지정 예시 추가 |

### 3. 다음 액션
- [ ] Alembic 자동화(도커 entrypoint 혹은 GH Actions) 설계
- [ ] 유저 도메인 Usecase + Auth 플로우 설계 및 테스트 작성


