# [Project Greg] 개발 변경 사항 (PM 보고용)
이 문서는 '구글 안티그래비티' 프로젝트의 3단계(추천 시스템 및 관리자 페이지) 개발 과정에서 변경된 모든 파일과 로직을 기록합니다.

---

## 1. 데이터베이스 스키마 변경 (`models.py`)
### 변경 목적
- **유료화 모델(BM) 도입**: 무료/유료 회원을 구분하기 위해 `users` 테이블 확장.
- **추천 알고리즘 도입**: 유저의 행동(조회, 찜 등)을 추적하기 위해 `user_actions` 테이블 신규 생성.

### 변경 내역
#### [MODIFY] `models.py`
1.  **`User` 테이블**: `subscription_level` 컬럼 추가 (Default: 'free')
2.  **`UserAction` 테이블**: 신규 추가 (Columns: `user_id`, `policy_id`, `action_type`, `timestamp`)
3.  **Relation**: `User`와 `UserAction` 간의 1:N 관계 설정 (`relationship` 활용)

---

## 2. 관리자(Admin) 대시보드 구축
### 구축 목적
- **데이터 기반 의사결정**: 전체 유저 수, 정책 수, 실시간 유저 행동 로그를 한눈에 파악.
- **보안 강화**: 일반 유저 페이지와 완전히 분리된 로그인/접속 환경 제공.

### 주요 기능 및 디자인 컨셉
#### A. 관리자 전용 로그인 (`/admin/login`)
- **보안 강조**: 일반 사용자가 접근했을 때 위화감을 느낄 수 있도록 **Dark Theme** 및 **"System Admin"** 경고 문구 적용.
- **접근 제어**: 별도의 관리자 인증(ID/PW) 절차 없이는 대시보드 접근 불가.

#### B. 관리자 대시보드 (`/admin/dashboard`)
- **ADMIN MODE Bar**: 상단에 붉은색 경고 바(**⚠️ ADMIN MODE ACTIVE**)를 배치하여 운영자에게 관리자 권한으로 접속 중임을 지속적으로 각인.
- **Left Sidebar UI**: 일반 페이지(Top Navbar)와 차별화된 **사이드바 레이아웃**으로 전문적인 관리 도구 느낌 강조.
- **실시간 통계**:
    1.  **Card UI**: 총 유저 수, 활성 정책 수, 시스템 부하 상태 표시.
    2.  **Live Log Table**: 유저들이 어떤 정책을 클릭하고 있는지 실시간 로그 조회 (`user_actions` 테이블 연동).

### 변경 파일 목록
- **[NEW] `routers/admin.py`**: 관리자 인증 및 대시보드 데이터 조회 백엔드 로직 (경로 수정: `templates/admin/` 폴더 참조).
- **[NEW] `templates/admin/login.html`**: 다크 모드 로그인 UI (구 `admin_login.html` 이동).
- **[NEW] `templates/admin/dashboard.html`**: 대시보드 메인 UI (구 `admin.html` 이동).
- **[NEW] `templates/admin/users.html`**: 유저 관리 페이지.
- **[NEW] `templates/admin/policies.html`**: 정책 콘텐츠 관리 페이지 (검색, 필터, 정렬 기능 포함).
- **[MODIFY] `main.py`**: 관리자 라우터(`admin.router`) 등록.

---

## 3. PM 전달 시 필수 포함 항목 (Deliverables CheckList)
PM님께 전달할 때는 다음 파일들과 **DB 변경 사항**을 반드시 함께 전달해야 합니다. 단순히 `admin.py`만 전달하면 작동하지 않습니다.

### A. 핵심 코드 파일
| 파일 경로 | 역할 | 비고 |
| :--- | :--- | :--- |
| **`routers/admin.py`** | 관리자 기능 핵심 로직 | 로그인, 검색, 수정, 통계 등 모든 백엔드 로직 |
| **`templates/admin/`** | 관리자 UI HTML 파일들 | `dashboard.html`, `users.html`, `policies.html`, `login.html` 전체 |
| **`models.py`** | DB 스키마 정의 | **`User`**, **`UserAction`** 모델 변경 및 추가 사항 포함 필수 |
| **`main.py`** | 앱 구동 및 라우터 설정 | `app.include_router(admin.router)` 한 줄이 없으면 접속 불가 |

### B. 데이터베이스(DB) 변경 요청 사항
코드를 배포하기 전에 실 운영 DB에 다음 SQL 작업이 선행되어야 합니다.

1. **`users` 테이블 컬럼 추가**:
   ```sql
   ALTER TABLE users ADD COLUMN subscription_level VARCHAR DEFAULT 'free';
   ALTER TABLE users ADD COLUMN region VARCHAR; -- (이미 있다면 생략)
   ```

2. **`users_action` 테이블 확인 (PM님 생성 테이블)**:
   - 코드를 PM님의 `users_action` 테이블 스키마에 맞춰 수정했습니다. 아래 컬럼들이 존재하는지 확인해주세요.
   ```sql
   -- 테이블명: users_action
   -- 컬럼:
   --   id (Integer)
   --   user_email (VARCHAR) -> users 테이블의 email과 연결
   --   policy_id (Integer) -> being_test 테이블의 id와 연결
   --   type (VARCHAR)
   --   created_at (TIMESTAMP)
   ```
   > **Note**: `models.py`가 위 스키마를 기준으로 작성되었습니다.

> **Note**: 위 항목들이 모두 반영되지 않으면 `500 Server Error`가 발생합니다.
