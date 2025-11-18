# 파일 트리

```text
.
├── app/ (Flask 애플리케이션 패키지 루트)
│   ├── __init__.py (Flask 앱/DB 초기화 진입점)
│   ├── admin.py (콘솔용 DB 리셋·데이터 관리 스크립트)
│   ├── routes/ (블루프린트 라우트 모듈)
│   │   ├── auth_routes.py (로그인, 로그아웃 등 인증 처리)
│   │   ├── attendance_routes.py (학생용 출석 체크/조회)
│   │   ├── database_routes.py (DB 데이터 확인용 디버그 페이지)
│   │   ├── main_routes.py (메인 페이지, 시간표 등 공통 페이지)
│   │   ├── professor_routes.py (교수용 출결/수업 관리)
│   |   └── timetable_routes.py (시간표 관련 페이지)
│   │   
│   ├── static/ (정적 파일)
│   │   ├── db.css (공통 테이블 스타일)
│   │   ├── style.css (기본 레이아웃 스타일 시트)
│   │   └── time_table.css (시간표 전용 스타일)
│   ├── templates/
│   │   ├── professor/
│   │   │   ├── lecture_list.html (교수 담당 과목 목록)
│   │   │   ├── manage_attendance_professor.html (출결 관리 페이지)
│   │   │   └── subject_sessions.html (과목별 수업 세션 목록)
│   │   ├── students/
│   │   │   ├── attendance_check.html (학생 오늘의 출석 체크)
│   │   │   ├── attendance_detail.html (과목별 상세 출결 내역)
│   │   │   └── manage_attendance_students.html (학생 전체 출결 현황)
│   │   ├── db.html (DB 데이터 확인용 템플릿)
│   │   ├── index.html (메인 화면)
│   │   ├── login.html (로그인 폼)
│   │   └── time_table.html (시간표)
│   ├── utils/
│   │   ├── auth.py (로그인 검증 데코레이터)
│   │   ├── attendance_helpers.py (출석 관련 헬퍼 함수)
│   │   ├── constants.py (학기, 출석 상태 등 상수 모음)
│   │   └── db_helpers.py (DB 연결 및 데이터 변환 헬퍼)
│   ├── services/ (추가 예정: 비즈니스 로직 계층)
│   │   └── (attendance_service.py – 출석 생성/검증 로직)
│   ├── repositories/ (추가 예정: DB 접근 추상화)
│   │   └── (attendance_repository.py – 출석/세션 쿼리 래퍼)
│   └── schemas/ (추가 예정: DTO/입력 검증 스키마)
│       └── (attendance_schema.py – 출석 요청 파라미터 검증)
├── config.py (환경 변수 및 DB 접속 설정)
├── database.md (DB 문서)
├── db/
│   └── create.sql (DB 생성 스크립트)
├── docker-compose.yml (개발용 MySQL 컨테이너 정의)
├── Dockerfile (애플리케이션 컨테이너 빌드 정의)
├── main.py (Flask 앱 실행 진입점)
├── README.md (프로젝트 개요)
├── requirements.txt (Python 의존성 목록)
├── tests/ (추가 예정: 자동화 테스트)
│   ├── (test_attendance_api.py – 출석 API 통합 테스트)
│   └── (test_repositories.py – DB 레이어 단위 테스트)
├── docs/ (추가 예정: 추가 문서)
│   └── (api.md – REST API 명세)
├── tree.md (파일 트리 문서)
└── venv/ (가상환경, 배포 시 제외)
    ├── Include/
    ├── Lib/
    │   └── site-packages/ (... 다수의 패키지 파일)
    ├── Scripts/
    │   └── (python.exe, pip.exe 등 실행 파일)
    └── pyvenv.cfg
```
