## 자료 Progress 확장 방안

### 1. 배경
- 현재 `user_progress` 테이블은 로드맵 항목(`roadmaps`)에 대해서만 완료 여부를 저장.
- 프론트 요청: 자료 학습 완료 여부도 동일한 API 흐름으로 보고 싶음.
- 자료(progress) 확장을 고민하는 단계.

### 2. 요구사항 정리
1. 로드맵 항목 완료/미완 로직 유지 (기존 API 영향 최소화).
2. 자료 완료 상태를 포함해 `/api/v1/progress` 조회 API에서 한 번에 통계 가능.
3. 자료 완료 토글 API 필요 여부 → 로드맵과 동일 패턴 선호(`POST /progress/{item_id}/complete`).
4. 향후 확장성: 다른 도메인(퀴즈, 챌린지 등)에도 동일한 구조로 적용 가능해야 함.

### 3. 설계 옵션 비교

| 옵션 | 설명 | 장점 | 단점 |
| --- | --- | --- | --- |
| A. 단일 `user_progress` 테이블에 `item_type` 컬럼 추가 | `item_type`(`roadmap`/`material`) + `item_id`로 식별 | - 스키마 최소 변경<br>- API 로직 재사용 | - FK 제약 직접 지정 어려움 (이종 테이블 참조)<br>- 참조 무결성은 애플리케이션 레벨로 검증 필요 |
| B. `user_progress` + `user_material_progress` 분리 | 로드맵/자료 각각 전용 테이블 | - FK 제약 명확<br>- 기존 로직 영향 최소 | - `/progress` API에서 두 테이블을 집계해야 함<br>- 토글 API를 별도로 나눠야 할 가능성 |
| C. 통합 Progress 테이블 + Polymorphic FK (SQLAlchemy joined table) | 부모 progress + 자식 progress_detail | - type-safe + FK 유지 | - 구조가 복잡, 향후 유지보수 부담 |

### 4. 선택: 옵션 A (단일 테이블 + item_type)
- 마이그레이션
  ```sql
  ALTER TABLE user_progress ADD COLUMN item_type VARCHAR(20) NOT NULL DEFAULT 'roadmap';
  ALTER TABLE user_progress ADD COLUMN material_id INTEGER NULL;
  -- roadmaps 진행 기록에 대해 item_type='roadmap', material_id NULL로 업데이트
  CREATE INDEX ix_user_progress_item_type ON user_progress(item_type);
  ```
- 앱 레벨 규칙
  - `item_type`이 `roadmap`이면 `roadmap_id` NOT NULL, `material_id` NULL.
  - `material`이면 `material_id` NOT NULL, `roadmap_id` NULL.
  - DB constraint는 `CHECK` 제약으로 보완:
    ```sql
    CHECK(
      (item_type = 'roadmap' AND roadmap_id IS NOT NULL AND material_id IS NULL) OR
      (item_type = 'material' AND material_id IS NOT NULL AND roadmap_id IS NULL)
    )
    ```
- API 변화
  - `POST /progress/{item_id}/complete`에 `type` 쿼리 파라미터 추가 (기본값 `roadmap`).
  - `/progress` 조회 시 `item_type`별 필터링, 통계 필드에 `material_total`, `material_completed` 추가.

### 5. 단계별 실행 계획
1. **마이그레이션**: `item_type`, `material_id`, CHECK 제약 추가. 기존 데이터 `item_type='roadmap'`으로 업데이트.
2. **Repository/Usecase 업데이트**:
   - `UserProgressRepository.upsert_progress`에 `item_type` 매개변수 추가.
   - 자료 progress 시 `roadmap_repository.exists` 대신 `material_repository.get_by_id`.
3. **API 스펙 수정**:
   - `POST /progress/{item_id}/complete?type=material`
   - `/progress` 응답에 `item_type` 필드 포함.
4. **프론트 연동**:
   - 자료 카드에서 완료 토글 → 위 API 호출.
   - 진도 화면에서 `category` 필터 외에 `type` 필터 추가 고려.
5. **테스트/문서**:
   - 기존 pytest 케이스 확장 (material progress).
   - README/API 문서, DOC_LOG 업데이트.

### 6. 향후 고려
- Material progress가 많아질 경우 통계 쿼리에 인덱스 추가 (`user_id + item_type`).
- Progress 히스토리가 필요하면 `completed_at` 변동 이력 테이블 별도 추가.
- 또 다른 도메인(퀴즈 등) 추가 시 `item_type` enum에 확장하고 동일 구조 활용.

