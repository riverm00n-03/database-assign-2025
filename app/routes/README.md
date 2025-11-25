# Routes 모듈 설명

이 디렉토리는 Flask 블루프린트 라우트 모듈들을 포함합니다. 각 파일은 특정 기능 영역의 라우트를 담당합니다.

## 파일 구조

### 인증 관련
- **auth_routes.py**: 사용자 인증 처리
  - `/login`: 로그인 페이지 및 로그인 처리
  - `/logout`: 로그아웃 처리

### 출석 관련
- **attendance_routes.py**: 학생용 출석 체크 및 조회
  - `/attendance/`: 오늘의 출석 체크 페이지
  - `/attendance/check`: 출석 체크 처리
  - `/attendance/manage`: 학생 전체 출결 현황
  - `/attendance/detail/<subject_id>`: 과목별 상세 출결 내역

### 교수 관련
- **professor_routes.py**: 교수용 출결 관리 및 수업 관리
  - `/professor/attendance`: 교수 담당 과목 목록
  - `/professor/subject/<subject_id>/sessions`: 과목별 수업 세션 목록
  - `/professor/cancel_session/<schedule_id>/<class_date>`: 휴강 처리
  - `/professor/uncancel_session/<session_id>`: 휴강 취소
  - `/professor/manage_attendance/<session_id>`: 출결 관리 페이지

### 시간표 관련
- **timetable_routes.py**: 시간표 조회 및 관리
  - `/timetable/`: 사용자 시간표 페이지 (학생/교수)

### 공통 페이지
- **main_routes.py**: 메인 페이지 및 공통 기능
  - `/`: 메인 페이지 (홈 화면)

### 개발/디버깅
- **database_routes.py**: 데이터베이스 데이터 확인용 (개발/디버깅 목적)
  - `/database/`: DB 데이터 HTML 페이지
  - `/database/show_database`: DB 데이터 JSON API

## 라우트 구조

각 라우트 파일은 Flask Blueprint를 사용하여 모듈화되어 있습니다:

```python
from flask import Blueprint

# Blueprint 생성
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 라우트 정의
@attendance_bp.route('/')
@login_required
def show_attendance():
    # 라우트 로직
    pass
```

## 주요 패턴

### 인증 확인
모든 보호된 라우트는 `@login_required` 데코레이터를 사용합니다:

```python
from app.utils.auth import login_required

@attendance_bp.route('/')
@login_required
def show_attendance():
    # 로그인된 사용자만 접근 가능
    pass
```

### 세션 정보 사용
세션 정보는 헬퍼 함수를 통해 가져옵니다:

```python
from app.utils.session_helpers import get_student_session_info

session_info = get_student_session_info()
username = session_info['username']
role = session_info['role']
student_number = session_info['student_number']
```

### 데이터베이스 연결
데이터베이스 연결은 헬퍼 함수를 사용합니다:

```python
from app.utils.db_helpers import get_db_connection

with get_db_connection() as conn:
    with conn.cursor(dictionary=True) as cursor:
        # 쿼리 실행
        pass
```

### 에러 처리
일반적으로 try-except 블록을 사용하여 에러를 처리합니다:

```python
try:
    # 로직 실행
    pass
except Exception as e:
    flash("오류가 발생했습니다.", "error")
    return redirect(url_for('main.root'))
```

## 역할별 접근 권한

- **학생 (student)**: 출석 체크, 출석 조회, 시간표 조회
- **교수 (professor)**: 출결 관리, 수업 세션 관리, 시간표 조회

역할 확인은 `session.get('role')`을 통해 수행됩니다.

