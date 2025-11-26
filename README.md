# Stacknori Backend

FastAPI 기반 학습 로드맵/자료 큐레이션 서비스의 백엔드 레포지토리입니다. Clean Architecture 계층 분리와 Docker 기반 실행 환경을 제공하며, DOC_LOG → Notion 자동화로 개발 로그를 관리합니다.

## 구조
```
app/
  core/            # 설정, DB 세션, 보안 유틸
  domain/          # 엔티티, 리포지토리 인터페이스
  infrastructure/  # 구체 리포지토리, 외부 어댑터
  usecases/        # 비즈니스 유스케이스
  presentation/    # FastAPI 라우터/스키마
Dockerfile         # multi-stage (dev/prod)
docker-compose.yml # api + postgres
scripts/           # 자동화 스크립트 (Notion sync 등)
```

## 빠른 시작
```bash
cp example.env .env
docker compose up --build
```
이후 `http://localhost:8000/docs`에서 API 스펙을 확인할 수 있습니다.

## 개발 시나리오
1. DOC_LOG.md 템플릿에 작업 내용을 기록
2. `git add DOC_LOG.md && git commit`
3. `git push` → GitHub Actions가 Notion Dev-Journal에 로그를 저장하고 DOC_LOG를 초기화

## 데이터베이스 마이그레이션
```bash
# 새 마이그레이션 생성
PYTHONPATH=. alembic revision -m "add something"

# 로컬에서 실행할 경우 호스트 DB URL을 지정
ALEMBIC_DATABASE_URL=postgresql+psycopg2://stacknori:stacknori@localhost:5432/stacknori alembic upgrade head
```
도커 컨테이너 내부에서는 `POSTGRES_SERVER=db` 환경 변수를 그대로 사용하면 된다.

## 초기 관리자 계정 생성
```bash
# 기본값으로 실행 (admin@stacknori.com / admin123456)
python scripts/seed_admin.py

# 환경 변수로 커스터마이징
ADMIN_EMAIL=admin@example.com \
ADMIN_PASSWORD=secure_password \
python scripts/seed_admin.py

# 도커 컨테이너 내부에서 실행
docker compose exec api python scripts/seed_admin.py
```
자세한 내용은 `docs/ROLE_SYSTEM.md`를 참고하세요.

## 테스트/배포 (로드맵)
- GitHub Actions CI (lint/test) & docker build 캐시
- NAS 기반 self-hosted runner에서 compose 배포 자동화

자세한 인프라/클린 아키텍처 계획은 `docs/INFRA_CLEAN_ARCH_PLAN.md`를 참고하세요.