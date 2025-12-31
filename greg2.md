# 통합 업무 보고 (PM 전달용)

본 문서는 Google Antigravity 세션에서 진행된 **데이터베이스 구축** 및 **소셜 로그인 연동** 작업의 통합 내역입니다.
PM님께 전달하여 프로젝트 Merge 시 참고할 수 있도록 구성하였습니다.

---

## 1. 작업 개요

- **기간**: 2025-12-23 ~ 2025-12-29
- **주요 내용**:
    1.  **DB 초기 구축**: `policies_remake.json` 데이터를 기반으로 한 `being_test` 테이블 생성 및 적재.
    2.  **OAuth 연동**: Google, Naver 소셜 로그인/회원가입 프로세스 구현 (Back/Front/Env).
    3.  **이슈 해결**: 인증 모달 및 로그인 상태 유지 관련 버그 수정.

---

## 2. 변경 파일 목록 (상세)

각 작업별로 추가되거나 수정된 파일의 리스트입니다.

### A. Database 구축 (12/23)

| 구분 | 파일 경로 | 설명 |
| :--- | :--- | :--- |
| **New** | `/apps/db_main_project/setup_db.py` | DB 테이블 생성 및 `policies_remake.json` 데이터 적재 스크립트 |
| **Mod** | `/apps/db_main_project/gemini.md` | 작업 이력 로그 (본 내용의 원본) |

> **주요 로직**:
> - `setup_db.py`를 실행하면 `Policy` 모델(being_test 테이블)이 없는 경우 생성하고, JSON 데이터를 파싱하여 적재합니다.
> - 지역명(`region`) 정규화 로직이 포함되어 있습니다.

### B. OAuth 소셜 로그인 연동 (12/29)

| 구분 | 파일 경로 | 설명 |
| :--- | :--- | :--- |
| **New** | `/apps/db_main_project/.env` | **[보안]** Google/Naver Client ID/Secret 및 JWT Secret 키 저장 |
| **Mod** | `/apps/db_main_project/routers/auth.py` | 소셜 로그인 (`/google`, `/naver`) 엔드포인트 및 콜백 로직 구현 |
| **Mod** | `/apps/db_main_project/static/script.js` | 소셜 로그인 버튼 핸들러(`socialLogin`) 및 토큰 처리 로직 추가 |
| **Mod** | `/apps/db_main_project/greg.md` | 1차 OAuth 연동 보고서 |

> **주요 로직**:
> - `auth.py`: `httpx`를 사용하여 소셜 공급자와 토큰 교환 후, 로컬 DB 유저 생성/로그인 처리.
> - `script.js`: 로그인 성공 후 리다이렉트된 URL 파라미터(`?social_login=success`)를 감지하여 메인 페이지로 이동.

### C. 기타 수기 변경 내역 (추가 확인)

| 구분 | 파일 경로 | 설명 |
| :--- | :--- | :--- |
| **New** | `/apps/db_main_project/routers/landing.py` | 랜딩 페이지 지도 통계용 API (`/api/landing/stats`) |
| **Mod** | `/apps/db_main_project/templates/landing.html` | 로그인 상태 체크 및 Auth 모달 연동 로직 추가 |

> **상세 내용**:
> - **landing.py**: `being_test` 테이블에서 지역별 개수를 집계하여 반환하는 API 구현.
> - **landing.html**: 
>   - 지도 클릭 시 `localStorage`의 `isLoggedIn` 상태를 확인.
>   - 비로그인 시 Auth 모달 팝업, 로그인 시 메인 페이지 이동 로직 적용.
>   - 디버깅용 `console.log` 추가.

---

## 3. 상세 코드 변경 사항 요약

### 1) setup_db.py (신규)
- `policies_remake.json` 파일 로드
- `normalize_region_name` 함수: 지역명 표준화 (예: '충청남도' -> '충남')
- `Policy` 모델 매핑 및 Bulk Insert

### 2) routers/auth.py (수정)
- **환경 변수 로드**: `os.getenv`로 .env 파일 내 키 로드.
- **Login API**: `RedirectResponse`를 통해 각 플랫폼 로그인 창으로 이동.
- **Callback API**: Authorization Code 수신 -> Access Token 요청 -> User Info 요청 -> DB 저장/조회 -> JWT 발급 -> Client 리다이렉트.

### 3) static/script.js (수정)
```javascript
// 소셜 로그인 버튼 클릭 시 이동
window.socialLogin = function(provider) { ... }

// 로그인 성공 복귀 후 처리
if (socialLogin === 'success') {
    alert(...);
    window.location.href = '/main.html';
}
```

### 4) routers/landing.py (신규)
- **API**: `/api/landing/stats`
- **기능**: DB에서 지역별 정책 개수를 `GROUP BY`로 집계하여 반환. 랜딩 페이지 지도의 숫자 카운터와 연동됨.

### 5) templates/landing.html (수정)
- **로그인 체크**: `localStorage.getItem('isLoggedIn')` 값에 따라 분기 처리.
- **이벤트 핸들러**: 지도 지역 클릭 시 비로그인 상태면 `window.openAuthModal` 호출.

---

## 4. 참고 사항

- **.env 파일**: 보안상 Git 등에 포함되지 않으므로, 서버 배포 시 `oauth_setup_guide.md` (별도 전달)를 참고하여 직접 생성해야 합니다.
- **DB 마이그레이션**: 현재 `Base.metadata.create_all` 방식을 사용 중이나, 추후 Alembic 도입 고려 가능합니다.
