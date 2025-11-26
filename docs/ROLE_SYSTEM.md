## Stacknori Role & Permission System

### 1. 현재 구현 상태

현재 시스템은 `is_superuser` 불린 필드를 사용하여 관리자 권한을 구분합니다.

#### User Model 필드
- `is_active`: 계정 활성화 여부
- `is_superuser`: 슈퍼유저(관리자) 여부

### 2. Role 시스템 설계

#### 2.1 Role Enum 정의
```python
class UserRole(str, Enum):
    USER = "user"           # 일반 사용자
    ADMIN = "admin"         # 관리자
    SUPERUSER = "superuser" # 슈퍼 관리자 (is_superuser와 호환)
```

#### 2.2 권한 매트릭스

| Role | 일반 API 접근 | 관리자 API 접근 | 시스템 설정 |
|------|--------------|----------------|------------|
| USER | ✅ | ❌ | ❌ |
| ADMIN | ✅ | ✅ | ❌ |
| SUPERUSER | ✅ | ✅ | ✅ |

### 3. 초기 Admin/Seed 전략

#### 3.1 Seed 스크립트
- 위치: `scripts/seed_admin.py`
- 목적: 초기 관리자 계정 생성
- 실행 방법:
  ```bash
  # 기본값으로 실행 (admin@stacknori.com / admin123456)
  python scripts/seed_admin.py

  # 환경 변수로 커스터마이징
  ADMIN_EMAIL=admin@example.com \
  ADMIN_PASSWORD=secure_password \
  python scripts/seed_admin.py

  # 기존 계정 강제 재생성
  FORCE_CREATE=true python scripts/seed_admin.py
  ```

#### 3.2 환경 변수
- `ADMIN_EMAIL`: 관리자 이메일 (기본값: `admin@stacknori.com`)
- `ADMIN_PASSWORD`: 관리자 비밀번호 (기본값: `admin123456`)
- `FORCE_CREATE`: 기존 계정 강제 재생성 여부 (기본값: `false`)

#### 3.3 Docker 통합
Docker entrypoint에서 마이그레이션 후 자동으로 seed를 실행할 수 있도록 확장 가능:
```bash
# scripts/docker-entrypoint.sh에 추가
if [ "$RUN_SEED" = "true" ]; then
  python scripts/seed_admin.py
fi
```

### 4. 향후 확장 계획

#### 4.1 Role 필드 추가
현재는 `is_superuser`만 사용하지만, 향후 `role` 필드를 추가하여 더 세밀한 권한 관리가 가능합니다:

```python
# 마이그레이션 예시
role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
```

#### 4.2 Permission 기반 접근 제어
- 각 API 엔드포인트에 필요한 권한 정의
- Dependency로 권한 체크 로직 구현
- 예: `@router.get("/admin/users", dependencies=[Depends(require_admin)])`

#### 4.3 Role 기반 의존성
```python
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### 5. 보안 고려사항

1. **초기 비밀번호 변경**: 프로덕션 환경에서는 반드시 초기 비밀번호를 변경해야 합니다.
2. **환경 변수 보호**: `.env` 파일에 민감한 정보를 저장하고 Git에 커밋하지 않습니다.
3. **강제 재생성**: `FORCE_CREATE=true`는 개발 환경에서만 사용하고, 프로덕션에서는 주의해야 합니다.

### 6. 테스트 전략

- Seed 스크립트 단위 테스트
- Role 기반 접근 제어 통합 테스트
- Admin API 엔드포인트 권한 검증 테스트

