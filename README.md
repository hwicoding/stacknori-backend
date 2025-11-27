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
# .env 파일에서 DATABASE_URL이 postgresql+asyncpg:// 형식인지 확인
docker compose up --build
```
이후 `http://localhost:8000/docs`에서 API 스펙을 확인할 수 있습니다.

### 중요: DATABASE_URL 형식
**반드시 비동기 드라이버를 사용해야 합니다:**
- ✅ 올바른 형식: `postgresql+asyncpg://user:password@host:port/dbname`
- ❌ 잘못된 형식: `postgresql://user:password@host:port/dbname` (동기 드라이버)

서버 환경에서는 `.env` 파일의 `DATABASE_URL`이 `postgresql+asyncpg://`로 시작하는지 확인하세요.

## 개발 시나리오
1. DOC_LOG.md 템플릿에 작업 내용을 기록
2. `git add DOC_LOG.md && git commit`
3. `git push` → GitHub Actions가 Notion Dev-Journal에 로그를 저장하고 DOC_LOG를 초기화

## API 개요

### 인증
- `POST /api/v1/auth/signup`: 회원가입
- `POST /api/v1/auth/login`: 로그인 (access/refresh token 발급)
- `POST /api/v1/auth/refresh`: 토큰 재발급
- `GET /api/v1/auth/me`: 현재 사용자 정보

### 로드맵
- `GET /api/v1/roadmaps`: 분야별 로드맵 계층 구조 + 사용자별 완료 상태

### 진도 관리
- `POST /api/v1/progress/{item_id}/complete?type=roadmap|material`: 로드맵/자료 완료 토글
  - `type` 파라미터: `roadmap` (기본값) 또는 `material`
  - 예시: `POST /api/v1/progress/1/complete?type=material` (자료 ID 1 완료 처리)
- `GET /api/v1/progress?type=roadmap|material&category=frontend|backend|devops`: 사용자 진도 현황 및 통계
  - `type`: 필터링할 progress 유형 (선택)
  - `category`: 로드맵 카테고리 필터 (선택)
  - 응답: `progress` (진도 목록), `statistics` (전체/로드맵/자료별 통계)

### 자료
- `GET /api/v1/materials?keyword=...&difficulty=beginner|intermediate&type=document|video&page=1&limit=20`: 자료 검색
- `POST /api/v1/materials/{material_id}/scrap`: 자료 스크랩
- `DELETE /api/v1/materials/{material_id}/scrap`: 자료 스크랩 해제

### API 사용 예제

```bash
# 1. 회원가입
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 2. 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# 3. 로드맵 조회 (토큰 필요)
curl -X GET http://localhost:8000/api/v1/roadmaps \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. 자료 완료 처리
curl -X POST http://localhost:8000/api/v1/progress/5/complete?type=material \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# 5. 진도 현황 조회 (자료만 필터)
curl -X GET "http://localhost:8000/api/v1/progress?type=material" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

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

## 로드맵/자료 시드 데이터
```bash
# 로드맵/자료 기본 데이터 입력
python scripts/seed_content.py

# 환경 변수로 DB URL 지정 가능
DATABASE_URL=postgresql+asyncpg://... python scripts/seed_content.py

# 도커 컨테이너 내부 실행
docker compose exec api python scripts/seed_content.py
```

## 테스트/배포 (로드맵)
- GitHub Actions CI (lint/test) & docker build 캐시
- NAS 기반 self-hosted runner에서 compose 배포 자동화

자세한 인프라/클린 아키텍처 계획은 `docs/INFRA_CLEAN_ARCH_PLAN.md`를 참고하세요.