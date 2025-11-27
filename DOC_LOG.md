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
- **Related Issue / Ticket**: N/A

### 1. 작업 요약
- GitHub Actions 배포 워크플로우 및 Notion Dev-Journal 워크플로우 실행 시험
- main 브랜치 push로 Self-hosted Runner 동작 확인

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | 초기에 Notion 속성 부재로 400 validation_error |
| 원인 분석 | Notion DB에 Date/Repository/Commit 속성이 없었음 |
| 선택한 해결책 | 해당 속성들을 Date, Rich Text 타입으로 생성 |
| 영향 범위/추가 조치 | 워크플로우 재실행 시 정상 완료, 추후 속성명 변경 금지 |

### 3. 다음 액션
- [ ] Dockerfile 재작성
- [ ] Clean Architecture 디렉토리 구조 설계


