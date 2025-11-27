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
- **Related Issue / Ticket**: 테스트 커버리지 향상

### 1. 작업 요약
- Roadmap/Material API 라우터 테스트 추가: `tests/test_roadmap_routes.py`, `tests/test_material_routes.py` 작성
- 라우터에서 엔티티→스키마 변환 로직 추가: `Roadmap` → `RoadmapNode`, `Material` → `MaterialItem` 변환 함수 구현
- SQLite JSON 컬럼 검색 이슈 해결: `keywords` 검색을 Python 레벨 필터링으로 변경하여 SQLite 호환성 확보
- 테스트 커버리지 81% → 86% 향상: 전체 테스트 스위트 32개 모두 통과

### 2. Troubleshooting & Decisions
| 항목 | 내용 |
| --- | --- |
| 이슈 | 라우터에서 `Roadmap`/`Material` 엔티티를 직접 반환 시 Pydantic ValidationError 발생 |
| 원인 분석 | `RoadmapListResponse`와 `MaterialListResponse`가 `RoadmapNode`/`MaterialItem` 스키마를 기대하지만 엔티티가 전달됨 |
| 선택한 해결책 | 라우터에 `_roadmap_to_node`, `_material_to_item` 변환 함수 추가하여 엔티티→스키마 변환 |
| 영향 범위/추가 조치 | Enum value 변환 로직 포함, 재귀적 children 변환 처리 |
| 이슈 | SQLite에서 `cast(MaterialModel.keywords, str).ilike()` 실행 시 `TypeError` 발생 |
| 원인 분석 | SQLite의 JSON 타입이 SQLAlchemy의 `cast`와 호환되지 않음 |
| 선택한 해결책 | `keywords` 검색을 Python 레벨 필터링으로 변경: DB에서는 title/summary만 검색, keywords는 메모리에서 필터링 |
| 영향 범위/추가 조치 | 대량 데이터에서는 성능 이슈 가능, 추후 PostgreSQL 전용 JSONB 검색으로 최적화 검토 |

### 3. 다음 액션
- [ ] Usecase/Repository 레벨 단위 테스트 추가 (현재 54-79% 커버리지)
- [ ] API 문서화 확장: OpenAPI 스키마에 예제 응답 추가 또는 별도 API 문서 페이지 생성 검토


