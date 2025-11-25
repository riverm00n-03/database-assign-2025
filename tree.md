# 파일 트리

```text
.
├── app/ (Flask 애플리케이션 패키지 루트)
│   ├── __init__.py (Flask 앱/DB 초기화 진입점)
│   ├── admin.py (Docker MySQL용 DB 리셋·데이터 관리 GUI 스크립트)
│   ├── admin_local.py (로컬 MySQL용 DB 리셋·데이터 관리 GUI 스크립트)
│   │
│   ├── routes/ (블루프린트 라우트 모듈)
│   │   ├── __init__.py (패키지 초기화)
│   │   ├── auth_routes.py (로그인, 로그아웃 등 인증 처리)
│   │   ├── attendance_routes.py (학생용 출석 체크/조회)
│   │   ├── database_routes.py (DB 데이터 확인용 디버그 페이지)
│   │   ├── main_routes.py (메인 페이지, 시간표 등 공통 페이지)
│   │   ├── professor_routes.py (교수용 출결/수업 관리)
│   │   ├── README.md (라우트 모듈 설명 문서)
│   │   └── timetable_routes.py (시간표 관련 페이지)
│   │
│   ├── utils/ (유틸리티 함수 모듈)
│   │   ├── __init__.py (패키지 초기화)
│   │   ├── auth.py (인증 관련: 로그인 데코레이터, 로그인 검증 함수)
│   │   ├── attendance_helpers.py (출석 관련 헬퍼 함수)
│   │   ├── attendance_test.py (출석 테스트 유틸리티)
│   │   ├── auto_absent.py (자동 결석 처리 유틸리티)
│   │   ├── constants.py (학기, 출석 상태, 요일 매핑 등 상수 모음)
│   │   ├── db_helpers.py (DB 연결 및 데이터 변환 헬퍼)
│   │   ├── README.md (유틸리티 모듈 설명 문서)
│   │   └── session_helpers.py (세션 정보 관리 헬퍼)
│   │
│   ├── static/ (정적 파일)
│   │   ├── attendance_cards.css (출석 관리 카드 스타일)
│   │   ├── attendance.css (출석 관련 스타일)
│   │   ├── common.css (공통 스타일)
│   │   ├── db.css (공통 테이블 스타일)
│   │   ├── login.css (로그인 페이지 스타일)
│   │   ├── manage_attendance.css (출석 관리 페이지 스타일)
│   │   ├── menu-icons.js (메뉴 아이콘 스크립트)
│   │   ├── navbar.css (네비게이션 바 스타일)
│   │   ├── navbar.js (네비게이션 바 스크립트)
│   │   ├── professor.css (교수 페이지 스타일)
│   │   ├── style.css (기본 레이아웃 스타일 시트)
│   │   └── time_table.css (시간표 전용 스타일)
│   │
│   ├── templates/ (Jinja2 템플릿)
│   │   ├── base.html (기본 레이아웃 템플릿)
│   │   ├── db.html (DB 데이터 확인용 템플릿)
│   │   ├── index.html (메인 화면)
│   │   ├── login.html (로그인 폼)
│   │   ├── time_table.html (시간표)
│   │   │
│   │   ├── professor/ (교수용 템플릿)
│   │   │   ├── lecture_list.html (교수 담당 과목 목록)
│   │   │   ├── manage_attendance_professor.html (출결 관리 페이지)
│   │   │   └── subject_sessions.html (과목별 수업 세션 목록)
│   │   │
│   │   └── students/ (학생용 템플릿)
│   │       ├── attendance_check.html (학생 오늘의 출석 체크)
│   │       ├── attendance_detail.html (과목별 상세 출결 내역)
│   │       └── manage_attendance_students.html (학생 전체 출결 현황)
│
├── config.py (환경 변수 및 DB 접속 설정)
├── database.md (DB 문서)
├── db/
│   └── create.sql (DB 생성 스크립트)
├── docker-compose.yml (개발용 MySQL 컨테이너 정의)
├── Dockerfile (애플리케이션 컨테이너 빌드 정의)
├── main.py (Flask 앱 실행 진입점)
├── README.md (프로젝트 개요)
├── requirements.txt (Python 의존성 목록)
├── scripts/ (스크립트 파일)
│   └── auto_absent_daily.py (일일 자동 결석 처리 스크립트)
├── tree.md (파일 트리 문서)
└── venv/ (가상환경, 배포 시 제외)
    ├── Include/
    ├── Lib/
    │   └── site-packages/ (... 다수의 패키지 파일)
    ├── Scripts/
    │   └── (python.exe, pip.exe 등 실행 파일)
    └── pyvenv.cfg
```

## 주요 디렉토리 구조 설명

### `app/routes/`
Flask 블루프린트 라우트 모듈들:
- **auth_routes.py**: 사용자 인증 (로그인/로그아웃)
- **attendance_routes.py**: 학생 출석 체크 및 조회 기능
- **database_routes.py**: 개발/디버깅용 DB 데이터 확인
- **main_routes.py**: 메인 페이지 및 공통 기능
- **professor_routes.py**: 교수용 출결 관리 및 수업 관리
- **timetable_routes.py**: 시간표 조회 및 관리

### `app/utils/`
재사용 가능한 유틸리티 함수들:
- **auth.py**: 인증 관련 (로그인 데코레이터, 로그인 검증)
- **attendance_helpers.py**: 출석 관련 헬퍼 함수 (출석 시간 범위 계산, 상태 포맷팅 등)
- **attendance_test.py**: 출석 테스트용 유틸리티
- **auto_absent.py**: 자동 결석 처리 로직
- **constants.py**: 애플리케이션 전역 상수 (학기 날짜, 출석 상태, 요일 매핑 등)
- **db_helpers.py**: 데이터베이스 연결 및 데이터 변환 헬퍼
- **session_helpers.py**: 세션 정보 관리 헬퍼

### `app/static/`
정적 파일 (CSS, JavaScript):
- **common.css**: 공통 스타일 (버튼, 카드, 테이블 등)
- **style.css**: 기본 레이아웃 스타일
- 각 페이지별 전용 CSS 파일들

### `app/templates/`
Jinja2 템플릿 파일들:
- **base.html**: 기본 레이아웃 템플릿
- **professor/**: 교수용 템플릿들
- **students/**: 학생용 템플릿들
