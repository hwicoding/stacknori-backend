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
- **Related Issue / Ticket**: Progress API 자료 확장

### 1. 작업 요약
- `user_progress` 테이블에 `item_type`/`material_id`/체크 제약을 추가하는 Alembic 마이그레이션 작성, ORM 모델도 Enum 기반으로 확장
- Progress Repository/Usecase/Router/Schema를 전부 업데이트해 `type=roadmap|material` 쿼리 파라미터, 통계(roadmap/material 별 집계)와 응답 필드를 통일
- 자료 완료 토글/조회 흐름을 검증하는 `tests/test_progress_routes.py`를 추가하고 기존 pytest 스위트 모두 통과
- README/API 문서에 progress API 확장 스펙 반영, DOC_LOG에 작업 내역 기록 후 Notion 동기화 예정

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | SQLite 테스트에서 `ck_user_progress_item_type` 제약 위반 발생 |
| 원인 분석 | SQLAlchemy Enum이 Enum 이름(`ROADMAP`)을 저장해 lower case 체크와 충돌 |
| 선택한 해결책 | `values_callable` 옵션으로 DB에 Enum value(`roadmap`)를 저장하도록 수정 |
| 영향 범위/추가 조치 | Postgres/SQLite 모두 동일한 문자열을 사용, 추후 Enum 확장 시 동일 패턴 적용 |
| 이슈 | Progress API 응답이 새 스키마(`item_type`, 세부 통계)를 만족하지 않아 ValidationError 발생 |
| 선택한 해결책 | Usecase에서 `UserProgress` → dict 변환 후 반환, Schemas에 `ProgressItemType` Enum 추가 |
| 영향 범위/추가 조치 | 프론트가 Roadmap/Material 구분을 한 번의 API에서 처리할 수 있어 UX 개선 |
| 이슈 | `type=material` 쿼리 파라미터 미지원으로 테스트 실패 |
| 선택한 해결책 | FastAPI Query alias를 `type`으로 지정해 기존 API 명세와 호환 |
| 영향 범위/추가 조치 | 기존 로드맵 클라이언트는 변화 없이 기본 `roadmap`으로 동작, 신규 자료 progress는 `?type=material` 호출만 추가하면 됨 |

### 3. 다음 액션
- [ ] CI 워크플로우에 새 progress 테스트 커버리지 리포트를 반영 (필요 시 단계 분리)
- [ ] 자료 progress 데이터를 활용한 통계/알림 요구사항 정리 (프론트 피드백 대기)


