## Stacknori Backend - Infra & Clean Architecture 준비 메모

### 1. 목표
- FastAPI 기반 클린 아키텍처 디렉토리 구조 정립 및 Docker 실행 환경 고도화.
- PostgreSQL 세션 관리, JWT 인증 파이프라인, CI/CD(Widgetbook/프런트 연동 전 단계) 준비.

### 2. 현재 상태 요약
- Docker 1단계: `stacknori_api`, `stacknori_db` 컨테이너 정상 기동(ports: `8000:8000`).
- Notion Dev-Journal 자동화 완료 → DOC_LOG 기반 로그 루틴 정착.
- requirements.txt에 핵심 패키지 기재, Clean Architecture 세부 구조 미정.

### 3. 작업 분류
#### 3.1 Docker/인프라
- [ ] multi-stage Dockerfile 작성 (dev/prod 분리: `uvicorn --reload` vs `gunicorn`).
- [ ] 환경 변수 관리: `.env`, `python-dotenv`, `secrets` 디렉토리.
- [ ] `docker-compose.yml` 개선: healthcheck, volume 명시, `depends_on` 조건, Restart policy.
- [ ] GitHub Actions: Docker build/test job 초안(추후 NAS 배포와 연계).

#### 3.2 Clean Architecture
- [ ] 디렉토리 스켈레톤
  ```
  app/
    core/   # config, security, deps
    domain/ # 엔티티, value object, repository 인터페이스
    usecases/
    infrastructure/
    presentation/ (routers)
  ```
- [ ] `app/core/config.py`에서 Pydantic Settings로 환경변수 로딩.
- [ ] DB Session Factory: SQLAlchemy 2.0 async + dependency (`get_db`).
- [ ] Repository 추상화: `domain/repositories/base.py`, 구현은 `infrastructure/repositories/...`.
- [ ] 유스케이스 계층: 서비스/인터랙터 단위 함수.

#### 3.3 JWT & 보안
- [ ] `core/security.py`: `create_access_token`, `verify_password`, `get_password_hash`.
- [ ] `domain/entities/user.py` + `schemas/user.py`: Pydantic 모델 분리.
- [ ] OAuth2 password flow 라우터 초안 (`presentation/routers/auth.py`).
- [ ] 테스트 사용자 seeding 전략 (Alembic seed script or management command).

### 4. 선행 TODO
1. 디렉토리 스켈레톤 + 초기파일 커밋 (빈 모듈 포함).
2. Dockerfile multi-stage, compose 개선.
3. DB 세션/Config/Settings 모듈 작성.
4. JWT/보안 유틸 구현 및 간단 헬스체크 라우터로 통합 테스트.

### 5. DOC_LOG 루틴
- 모든 단계별 변경사항은 `DOC_LOG.md` 템플릿에 맞춰 작성 후 push → Notion 기록.
- Troubleshooting 발생 시 `2. Troubleshooting & Decisions` 표에 원인/결정/영향을 즉시 기록.


