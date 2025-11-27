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
- **Related Issue / Ticket**: DOC_LOG → Notion 스타일 개선

### 1. 작업 요약
- Notion Dev-Journal의 `Date/Repository/Commit` 컬럼을 자동 채우도록 `scripts/notion_sync.py`를 확장, DOC_LOG 메타 정보와 GitHub env를 파싱해 날짜·저장소 링크·커밋 링크를 모두 세팅
- Notion에 링크 텍스트/아이콘이 적용되도록 Repository/Commit을 Rich text(깃허브 URL)로 구성, 날짜는 ISO 포맷으로 변환해 정렬이 가능한 date 속성으로 저장

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | Notion DB에 Date/Repository/Commit 컬럼을 만들었지만 자동화가 값을 채우지 않아 수동 입력이 필요했음 |
| 원인 분석 | 기존 스크립트가 `Name`/본문 block만 생성하고 데이터베이스 속성은 사용하지 않음 |
| 선택한 해결책 | DOC_LOG `0. 메타` 섹션에서 key/value를 파싱하고, 깃허브 환경 변수(`GITHUB_REPOSITORY`, `GITHUB_SHA`)를 조합해 해당 컬럼 값을 구성 |
| 영향 범위/추가 조치 | 앞으로 생성되는 모든 페이지가 표 형태 메타 + DB 컬럼 값을 동시에 갖게 되어 정렬/필터가 가능, 추가 컬럼 필요 시 동일 방식으로 확장 예정 |

### 3. 다음 액션
- [ ] 자료 progress 통합 마이그레이션 및 API 구현
- [ ] CI에 새 API 통합 테스트 추가 및 문서화 자동화(Notion)에 API 변경 내역 연동


