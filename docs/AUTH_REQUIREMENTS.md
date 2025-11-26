## Stacknori Auth & User Usecase 설계 메모

### 1. 목표
- FastAPI 기반 API에서 안전한 이메일/비밀번호 인증과 토큰 발급 흐름 구축
- Clean Architecture 흐름을 유지하며 `domain → usecases → presentation` 계층으로 나누기
- JWT Access/Refresh 토큰 전략 명확히 정의, 만료/재발급 정책 포함

### 2. 엔드포인트 후보
| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/auth/signup` | 신규 사용자 생성 |
| POST | `/api/auth/login` | 이메일/비밀번호 인증, Access/Refresh 토큰 발급 |
| POST | `/api/auth/refresh` | Refresh 토큰 검증 후 Access 토큰 재발급 |
| GET | `/api/users/me` | 현재 사용자 정보 조회 |
| PATCH | `/api/users/me` | 프로필/비밀번호 갱신 (후순위) |

### 3. 토큰 전략
> [!INFO] Access 토큰 15~30분, Refresh 토큰 14~30일 권장. 토큰은 모두 JWT 사용.

| 구분 | Access Token | Refresh Token |
| --- | --- | --- |
| 만료 | 30분 | 14일 |
| 페이로드 | `sub`, `exp`, `type="access"` | `sub`, `exp`, `type="refresh"` |
| 저장 위치 | 클라이언트 메모리/헤더 | 안전 저장소(secure store) |
| 회수 전략 | 블랙리스트 미도입 (단순 만료) | Refresh 사용 시 즉시 재발급 & 기존 무효 처리(optional) |

### 4. 유즈케이스 분리
1. `RegisterUserUseCase`
   - 입력: email, password
   - 검증: 중복 이메일 체크
   - 출력: User DTO (id, email, timestamps)

2. `AuthenticateUserUseCase`
   - 입력: email, password
   - 절차: 사용자 조회 → password verify → 토큰 생성
   - 출력: `TokenPair(access_token, refresh_token, token_type)`

3. `RefreshTokenUseCase`
   - 입력: refresh_token
   - 검증: JWT decode + `type=refresh`
   - 출력: 신규 Access Token (+선택적으로 Refresh 재발급)

4. `GetCurrentUserUseCase`
   - 입력: access_token
   - 절차: JWT decode → 사용자 조회 → User DTO

### 5. 의존성/계층별 계획
- `app/domain/entities/user.py`: 비밀번호 해시 저장(`hashed_password`), Role/권한 필드 후속 확장 고려
- `app/usecases/auth.py` (신규): 상기 유즈케이스 구현
- `app/presentation/api/v1/routes/auth.py`: FastAPI 라우터, OAuth2PasswordRequestForm 지원
- `app/core/security.py`:  
  - `create_access_token(subject, expires_delta)`  
  - `create_refresh_token(subject, expires_delta)`  
  - `decode_token(token, expected_type)`
- `app/core/dependencies.py`: `get_current_user` dependency

### 6. 테스트 전략
- `tests/usecases/test_auth.py`: 유효/잘못된 비밀번호, refresh 흐름 케이스
- `tests/api/test_auth_routes.py`: TestClient 기반 e2e (나중에)

### 7. TODO 체크리스트
- [ ] Password hashing/verify 유틸 정리 (`core/security`)
- [ ] Auth usecase 모듈 생성 및 단위 테스트
- [ ] Auth Router + Pydantic Schemas (`schemas/auth.py`)
- [ ] DOC_LOG 기록 & Notion 싱크

