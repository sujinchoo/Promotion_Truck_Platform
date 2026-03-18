# 화물차 광고 플랫폼 MVP

신뢰 중심의 화물차 광고/상담 플랫폼을 **GitHub + Render + Flask + PostgreSQL** 기반으로 시작하기 위한 첫 번째 MVP입니다.

## 1. 목표

이 MVP의 목적은 아래 4가지를 오늘 바로 동작시키는 것입니다.

- 랜딩페이지
- 문의 폼
- 관리자 페이지
- PostgreSQL(DB) 저장

디자인 방향은 **파란색 톤의 안정감**, **과하지 않은 광고 느낌**, **기사님/드라이버에게 신뢰를 주는 구조**입니다.

---

## 2. 현재 포함된 기능

### 랜딩페이지
- 신뢰 중심 카피
- CTA 버튼
- 서비스 소개 카드
- 상담 신청 섹션

### 문의 폼
- 이름
- 연락처
- 지역
- 업종/용도
- 관심 차종
- 예산
- 연락 가능한 시간
- 추가 요청사항
- UTM 저장용 hidden field

### 관리자 페이지
- 전체 리드 확인
- 최근 접수 리드 목록 확인
- 기본 통계(총 리드 수 / 신규 리드 수)

### DB 저장
- Flask + SQLAlchemy
- Render PostgreSQL 연결 가능
- 로컬에서는 SQLite로도 빠르게 테스트 가능

---

## 3. 폴더 구조

```bash
truck-lead-mvp/
├─ app.py
├─ config.py
├─ models.py
├─ requirements.txt
├─ Procfile
├─ render.yaml
├─ .env.example
├─ static/
│  └─ css/
│     └─ style.css
└─ templates/
   ├─ base.html
   ├─ index.html
   ├─ admin.html
   └─ thank_you.html
```

---

## 4. DB 스키마

`Lead` 테이블 주요 컬럼:

- id
- created_at
- name
- phone
- region
- business_type
- vehicle_type
- budget
- contact_time
- message
- status
- utm_source
- utm_medium
- utm_campaign
- referrer
- ip_address

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

`.env.example`를 참고해서 `.env` 작성:

```env
SECRET_KEY=change-me
DATABASE_URL=postgresql://username:password@host:5432/database
```

PostgreSQL이 없으면 일단 비워두고 SQLite로 테스트해도 됩니다.

### 5-4. 실행

```bash
python app.py
```

브라우저에서 아래 경로 확인:

- 메인: `http://127.0.0.1:5000/`
- 관리자: `http://127.0.0.1:5000/admin`

---

## 6. Render 배포용 설정

이 프로젝트에는 아래 배포 파일이 포함되어 있습니다.

- `Procfile`
- `render.yaml`

### Render에서 할 일

1. GitHub에 저장소 업로드
2. Render에서 **New + Blueprint** 또는 **New Web Service** 선택
3. 저장소 연결
4. `render.yaml` 사용 또는 아래 값 수동 입력

#### Web Service 예시
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

#### 환경변수
- `SECRET_KEY`
- `DATABASE_URL` (Render Postgres 연결 문자열)

---

## 7. 오늘 이후 바로 붙일 기능

우선순위는 아래 순서가 좋습니다.

### 1차
- Google Sheets 동기화
- Telegram 알림 전송
- 관리자 로그인

### 2차
- 리드 상태 변경
- 검색/필터
- UTM 대시보드

### 3차
- 유튜브 업로드 연동
- 네이버 블로그 자동화/반자동화
- 광고 성과 리포트

---

## 8. 디자인 원칙

- 화려한 광고 톤보다 **안정감**
- 기사님/드라이버에게 **실제 상담 가능성** 전달
- 모바일에서도 빠르게 문의 가능
- 읽기 쉬운 문장과 단정한 카드 UI
- 파란색 계열 중심으로 **신뢰감 있는 브랜드 인상** 유지

---

## 9. 운영 시 주의사항

실서비스 전환 전에는 아래를 반드시 추가해야 합니다.

- 개인정보처리방침 페이지
- 개인정보 수집/이용 동의 문구
- 관리자 인증 로그인
- 스팸 방지(예: reCAPTCHA 또는 서버 검증)
- 알림 연동(Telegram/메일)
- 로그 기록

---

## 10. 다음 작업 제안

다음 단계는 아래 중 하나로 바로 이어갈 수 있습니다.

1. **Google Sheets 저장 기능 추가**
2. **Telegram 실시간 알림 추가**
3. **관리자 로그인 기능 추가**
4. **차종별 상세 랜딩페이지 추가**

