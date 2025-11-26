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
- `.env` 기준으로 `docker compose up --build` 실행, FastAPI/DB 컨테이너 정상 기동 확인
- `/health`, `/docs` 모두 200 응답이며 환경 값 `development` 노출로 dev 모드 검증 완료

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | Docker daemon not running → `Cannot connect to the Docker daemon` |
| 원인 분석 | 로컬 Mac에서 Docker Desktop이 꺼져 있었음 |
| 선택한 해결책 | Docker Desktop 실행 후 동일 명령 재시도 |
| 영향 범위/추가 조치 | 빌드/기동 성공, DOC_LOG에 런북화. 향후 실행 전 데몬 상태 확인 습관화 |

### 3. 다음 액션
- [ ] Alembic 초기화 및 기본 마이그레이션
- [ ] 실제 도메인/리포지토리 구현 및 auth 플로우 설계



