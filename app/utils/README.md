# Utils 모듈 설명

이 디렉토리는 애플리케이션 전반에서 사용되는 재사용 가능한 유틸리티 함수들을 포함합니다.

## 파일 구조

### 인증 관련
- **auth.py**: 인증 관련 유틸리티
  - `login_required`: 로그인 확인 데코레이터
  - `login_user`: 학생 학번으로 로그인 검증

### 출석 관련
- **attendance_helpers.py**: 출석 관련 헬퍼 함수
  - `get_attendance_window`: 출석 가능 시간 범위 계산
  - `format_attendance_status`: 출석 상태 코드를 한글 표시명으로 변환
  - `calculate_week_dates`: 각 스케줄의 첫 번째 수업 날짜 계산
  - `build_session_map`: 세션 데이터를 딕셔너리로 매핑
  - `calculate_weeks_info`: 학기 주차 정보 계산

- **attendance_test.py**: 출석 테스트용 유틸리티
  - 테스트 환경에서 시간을 조작하기 위한 함수

- **auto_absent.py**: 자동 결석 처리 유틸리티
  - `mark_absent_for_missing_checkins`: 미출석 학생 자동 결석 처리
  - `run_daily_auto_absent`: 일일 자동 결석 처리 실행

### 데이터베이스 관련
- **db_helpers.py**: 데이터베이스 연결 및 데이터 변환 헬퍼
  - `get_db_connection`: UTF-8 인코딩 설정이 포함된 DB 연결 생성
  - `to_time`: 다양한 형식의 시간 값을 time 객체로 변환
  - `format_time_to_str`: time 객체를 HH:MM 형식 문자열로 변환
  - `format_timedelta_to_str`: timedelta 객체를 HH:MM:SS 형식 문자열로 변환
  - `get_student_id_by_number`: 학번으로 학생 ID 조회
  - `get_or_create_session`: 수업 세션 조회/생성
  - `get_subject_info`: 과목 정보 조회
  - `get_subject_name`: 과목 이름 조회
  - `get_student_enrolled_subjects`: 학생 수강 과목 목록 조회

### 세션 관련
- **session_helpers.py**: 세션 정보 관리 헬퍼
  - `get_session_info`: 일반 사용자 세션 정보 조회
  - `get_student_session_info`: 학생 세션 정보 조회

### 상수
- **constants.py**: 애플리케이션 전역 상수
  - `ATTENDANCE_WINDOW_MINUTES`: 출석 가능 시간 범위 (분)
  - `MAX_WEEKS_PER_SEMESTER`: 학기당 최대 주차 수
  - `SEMESTER_1_START_MONTH`, `SEMESTER_1_END_MONTH`: 1학기 날짜 설정
  - `SEMESTER_2_START_MONTH`, `SEMESTER_2_END_MONTH`: 2학기 날짜 설정
  - `get_semester_dates`: 학기 시작일과 종료일 반환
  - `WEEKDAY_MAP`: 요일 문자열을 Python weekday 숫자로 매핑
  - `WEEKDAY_TO_STR`: Python weekday 숫자를 요일 문자열로 매핑
  - `KOREAN_TO_WEEKDAY`: 한글 요일을 영문 요일로 매핑
  - `WEEKDAY_NAMES`: 요일 이름 리스트
  - `ATTENDANCE_STATUS_MAP`: 출석 상태 코드를 한글 표시명으로 매핑 (상세 페이지용)
  - `ATTENDANCE_STATUS_DISPLAY`: 출석 상태 코드를 한글 표시명으로 매핑 (관리 페이지용)

## 사용 가이드

### 인증 데코레이터 사용
```python
from app.utils.auth import login_required

@login_required
def my_view():
    # 로그인된 사용자만 접근 가능
    pass
```

### 세션 정보 가져오기
```python
from app.utils.session_helpers import get_student_session_info

session_info = get_student_session_info()
username = session_info['username']
role = session_info['role']
student_number = session_info['student_number']
```

### 데이터베이스 연결
```python
from app.utils.db_helpers import get_db_connection

with get_db_connection() as conn:
    with conn.cursor(dictionary=True) as cursor:
        # 쿼리 실행
        pass
```

### 시간 변환
```python
from app.utils.db_helpers import to_time, format_time_to_str

# DB에서 가져온 시간 값을 time 객체로 변환
start_time = to_time(row['start_time'])

# time 객체를 문자열로 변환
time_str = format_time_to_str(start_time)
```

### 상수 사용
```python
from app.utils.constants import WEEKDAY_MAP, get_semester_dates

# 요일 매핑
weekday_num = WEEKDAY_MAP['MON']  # 0

# 학기 날짜 가져오기
start_date, end_date = get_semester_dates(2025, 2)  # 2025년 2학기
```

