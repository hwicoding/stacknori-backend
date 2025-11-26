## Stacknori DOC Log

### 1. 작업 배경
- NAS 환경(`/home/iwh/stacknori`)에 `hwicoding/stacknori-backend`를 클론하여 백엔드 전용 인프라를 재구축.
- 기존 임시 백엔드 디렉토리는 `backend_old`로 백업해 롤백 경로 확보.
- `requirements.txt`에 FastAPI · SQLAlchemy · Alembic · JWT · 이메일 검증 등 Clean Architecture 기반 핵심 의존성을 정리함.

### 2. Notion Dev-Journal 연동 준비
- Private Integration: `Stacknori Dev-Journal (Internal Integration)` 생성 및 개발 일지 페이지에 초대 완료.
- `NOTION_API_KEY`, `NOTION_DATABASE_ID`를 백엔드/프런트 GitHub Secrets에 저장해 단일 키로 양측에서 활용 가능하게 구성.
- 무료 워크스페이스에서도 Integration 수 제한이 없어 동일 키 재사용에 제약 없음.

### 3. Docker 인프라 1단계 구축 현황
- `docker-compose.yml`: `web` 서비스에 `gunicorn` 기반 실행, `ports: "8000:8000"` 매핑으로 외부 접근 가능하도록 구성.
- `backend/Dockerfile`: `python:3.11-slim` 베이스, `fastapi`, `uvicorn`, `gunicorn`, `python-dotenv`, `psycopg2-binary` 설치 후 8000 포트 노출.
- 컨테이너 상태
  - `stacknori_api`: FastAPI 서버, 컨테이너 내부 8000 포트에서 구동.
  - `stacknori_db`: PostgreSQL, 데이터 볼륨 마운트 완료.
- 개발 PC에서 `http://100.88.40.125:8000/docs` 접속 예정(포트 포워딩 완료).

### 4. Troubleshooting 기록
| 이슈 | 원인 | 해결 |
| --- | --- | --- |
| `docker compose` unknown command | Ubuntu 환경에서 구버전 `docker-compose`만 설치됨 | `sudo docker-compose up -d`로 명령어 수정 |
| `Dockerfile: no such file` | `backend/` 디렉토리에 Dockerfile 부재 | Dockerfile 및 임시 `app/main.py` 생성 |
| `gunicorn: no such file or directory` | Dockerfile에서 `gunicorn` 미설치 | `RUN pip install ... gunicorn` 후 재빌드 |
| `KeyError: 'ContainerConfig'` | 구버전 docker-compose 메타데이터 충돌 | `docker-compose down && docker rmi`로 초기화 후 재실행 |

### 5. Notion 자동화 전략 정리
- 커밋/작업 내역을 `DOC_LOG.md`에 마크다운 템플릿으로 작성.
- GitHub Actions 트리거: `push` 시 `DOC_LOG.md` 파싱 → Notion DB에 페이지 생성 → 성공 시 `DOC_LOG.md` 초기화.
- Git 커밋 메시지는 간결하게 유지하고, 세부 의사결정 로그는 Notion에서 관리.

### 6. 향후 액션 아이템
1. 각 레포 루트에 `DOC_LOG.md` 템플릿 고도화 및 공통 규칙 문서화.
2. GitHub Actions 워크플로우(YAML) 작성 및 Notion API 호출 로직 구현/테스트.
3. Dockerfile 개선, Clean Architecture 디렉토리/DB 세션/JWT 구현.
4. 프런트/Widgetbook 레포를 로컬 PC에 클론하여 동일 Notion Integration으로 로그 공유.

### 7. GitHub Actions/Notion 연동 트러블슈팅
| 이슈 | 원인 | 해결 |
| --- | --- | --- |
| 워크플로우 push 거부 | Sourcetree OAuth 토큰에 `workflow` 스코프 부재 | `workflow` 권한 포함 토큰으로 인증 후 재송신 |
| Notion 404 (DB 미탐색) | 페이지 링크 사용, Integration 미공유 | DB 뷰 ID 확인 및 `Stacknori Dev-Journal` Integration 초대 |
| Notion 400 (`Name` 미존재) | Notion 테이블 핵심 컬럼명이 `이름`으로 설정됨 | 제목 컬럼을 `Name`으로 변경하여 API 속성과 일치 |
| 자동 초기화 커밋 실패(403) | 기본 `GITHUB_TOKEN`이 `read` 권한만 보유 | 워크플로우에 `permissions: contents: write` 추가하여 push 허용 |
