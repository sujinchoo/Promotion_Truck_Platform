# 화물차 광고 플랫폼 MVP

신뢰 중심의 화물차 광고/상담 플랫폼을 **GitHub + Render + Flask + PostgreSQL** 기반으로 운영하기 위한 MVP입니다.

## 1. 목표

이 MVP의 핵심 목표는 아래 기능을 안전하게 운영하는 것입니다.

- 랜딩페이지
- 모바일 전용 상담 랜딩
- 문의 폼 및 개인정보 동의
- 관리자 페이지
- Render PostgreSQL(DB) 저장

---

## 2. 현재 포함된 기능

### 랜딩페이지
- 메인 랜딩페이지
- 모바일 광고 전용 랜딩페이지
- 상담 CTA 버튼
- 서비스 소개 카드
- 개인정보처리방침 / 개인정보 수집·이용 안내 페이지

### 문의 폼
- 이름
- 연락처
- 지역
- 관심 차종
- 추가 요청사항
- 개인정보 수집·이용 및 통합 상담 동의
- UTM 저장용 hidden field

### 관리자 페이지
- 전체 리드 확인
- 최근 접수 리드 목록 확인
- 기본 통계(총 리드 수 / 신규 리드 수 / 모바일 리드 수)
- Render 환경변수 기반 관리자 로그인

### DB 저장
- Flask + SQLAlchemy
- Render PostgreSQL 연결
- 로컬에서는 SQLite로 빠르게 테스트 가능
- 운영 시 DB URL은 Render 환경변수로만 주입

---

## 3. 개인정보 및 상담 운영 정책

- 상담은 **씨앤제이컴퍼니**를 통하여 진행됩니다.
- 입력된 데이터는 상담 진행과 후속 관리 목적으로만 사용됩니다.
- 상담 신청서 내용은 자동 저장 및 관리됩니다.
- 데이터 저장 위치는 **Render 클라우드 환경**입니다.
- 동일한 회사 직원이 차량상담, 특장상담, 보험견적 등 통합 상담을 진행합니다.
- 통합 상담을 위해 필요한 범위에서 개인정보 제3자 제공이 가능함을 고지합니다.
- 본 서비스에는 구글 로그인 및 기타 외부 로그인 기능이 없습니다.

---

## 4. 폴더 구조

```bash
Promotion_Truck_Platform/
├─ app.py
├─ config.py
├─ models.py
├─ requirements.txt
├─ Procfile
├─ render.yaml
├─ static/
│  ├─ css/style.css
│  └─ images/
└─ templates/
   ├─ base.html
   ├─ index.html
   ├─ mobile.html
   ├─ privacy.html
   ├─ privacy_consent.html
   ├─ admin.html
   ├─ admin_login.html
   ├─ thank_you.html
   └─ partials/consult_form.html
```

---

## 5. 로컬 실행 방법

### 5-1. 가상환경 생성

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# 또는
.venv\Scripts\activate      # Windows
```

### 5-2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5-3. 환경변수 설정

운영용 식별정보, 관리자 계정, DB URL은 코드에 하드코딩하지 않고 환경변수로만 관리합니다.

```env
SECRET_KEY=change-me
DATABASE_URL=postgresql://username:password@host:5432/database
ADMIN_USERNAME=your-admin-id
ADMIN_PASSWORD=your-admin-password
```

`DATABASE_URL`이 없으면 로컬에서는 SQLite(`truck_leads.db`)로 실행됩니다.

### 5-4. 실행

```bash
python app.py
```

브라우저에서 아래 경로 확인:

- 메인: `http://127.0.0.1:5000/`
- 모바일 랜딩: `http://127.0.0.1:5000/mobile`
- 개인정보처리방침: `http://127.0.0.1:5000/privacy`
- 개인정보 수집·이용 안내: `http://127.0.0.1:5000/privacy-consent`
- 관리자: `http://127.0.0.1:5000/admin`

---

## 6. Render 배포용 설정

이 프로젝트는 Render 배포를 기준으로 구성되어 있습니다.

### Render 환경변수
- `SECRET_KEY`
- `DATABASE_URL`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

### Render에서 할 일
1. GitHub에 저장소 업로드
2. Render에서 **New + Blueprint** 또는 **New Web Service** 선택
3. 저장소 연결
4. `render.yaml` 기준으로 배포
5. 관리자 계정은 Render Dashboard의 Environment에서 직접 입력

---

## 7. 운영 시 주의사항

- 코드에 내부 URL, 계정 ID, 비밀번호 등 식별정보를 남기지 않습니다.
- 운영 전 개인정보처리방침과 개인정보 수집·이용 안내 문구를 반드시 검토합니다.
- 관리자 환경변수가 없으면 `/admin/login`은 503으로 차단됩니다.
- 실서비스 전환 전 스팸 방지, 알림 연동, 로그 정책을 추가 검토해야 합니다.

---

## 8. 참고

개인정보처리방침 문안 구성은 기존 운영 중인 페이지를 참고하여 본 서비스 구조에 맞게 재작성했습니다: `https://tprboard.onrender.com/privacy`
