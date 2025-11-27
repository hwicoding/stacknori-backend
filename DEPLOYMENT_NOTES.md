# 배포 환경 설정 가이드

## DATABASE_URL 설정 (중요)

FastAPI는 비동기 SQLAlchemy를 사용하므로, **반드시 비동기 드라이버를 사용해야 합니다**.

### 올바른 형식
```bash
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}
```

### 예시
```bash
DATABASE_URL=postgresql+asyncpg://stacknori:stacknori@db:5432/stacknori
```

### 잘못된 형식 (사용하지 마세요)
```bash
# ❌ 동기 드라이버 - 컨테이너가 재시작됩니다
DATABASE_URL=postgresql://stacknori:stacknori@db:5432/stacknori
```

## 서버 환경 변수 확인

NAS 서버의 `/home/iwh/stacknori/backend/.env` 파일에서 다음을 확인하세요:

1. `DATABASE_URL`이 `postgresql+asyncpg://`로 시작하는지 확인
2. 환경 변수 치환이 올바르게 작동하는지 확인

### .env 파일 예시
```bash
# Database
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=stacknori
POSTGRES_PASSWORD=stacknori
POSTGRES_DB=stacknori
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}
```

## 문제 해결

컨테이너가 계속 재시작되는 경우:

1. `.env` 파일의 `DATABASE_URL` 확인
2. 컨테이너 로그 확인: `docker-compose logs api`
3. 환경 변수가 올바르게 로드되었는지 확인: `docker-compose exec api env | grep DATABASE_URL`

## 참고

- Alembic 마이그레이션은 동기 드라이버(`postgresql+psycopg2`)를 사용합니다
- 애플리케이션 코드는 비동기 드라이버(`postgresql+asyncpg`)를 사용합니다
- `docker-entrypoint.sh`에서 Alembic용 `ALEMBIC_DATABASE_URL`을 자동으로 변환합니다

