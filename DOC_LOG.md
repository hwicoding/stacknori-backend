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
- **Related Issue / Ticket**: Frontend API integration follow-up

### 1. 작업 요약
- DOC_LOG GitHub Actions 반복 실행 문제 해결: workflow에 `github.actor != 'github-actions[bot]'` 조건 추가해 자동 커밋이 재트리거되지 않도록 단일화
- 자료 progress 확장 설계안(`docs/PROGRESS_EXPANSION_PLAN.md`) 작성: `user_progress`에 `item_type`/`material_id`를 추가해 로드맵·자료를 단일 테이블로 관리하는 방향 확정

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | DOC_LOG Sync 워크플로우가 자체 커밋으로 워크플로우를 다시 호출해 Actions가 3번씩 실행됨 |
| 원인 분석 | `git-auto-commit-action`의 push가 다시 main 업데이트로 인식됨 |
| 선택한 해결책 | 워크플로우에 `if: github.actor != 'github-actions[bot]'` 조건 추가하여 자동 커밋이 있을 때 job을 스킵 |
| 영향 범위/추가 조치 | 이제 push 당 Run Tests + DOC_LOG가 한 번씩만 실행됨, 필요 시 추후 완전 통합 고려 |
| 이슈 | 자료 완료(progress) 처리 방식을 결정해야 함 |
| 선택한 해결책 | `item_type` 기반 단일 progress 테이블 유지(옵션 A) + `type` 파라미터로 API 확장 계획 수립 |
| 영향 범위/추가 조치 | 마이그레이션/Repository/API 수정 로드맵 마련, 이후 구현 단계에서 적용 |

### 3. 다음 액션
- [ ] 자료 progress 통합 마이그레이션 및 API 구현
- [ ] CI에 새 API 통합 테스트 추가 및 문서화 자동화(Notion)에 API 변경 내역 연동


