"""
애플리케이션 상수 정의
"""
from datetime import date

# 출석 관련 상수
ATTENDANCE_WINDOW_MINUTES = 10  # 출석 가능 시간 범위 (분 단위)
MAX_WEEKS_PER_SEMESTER = 16  # 학기당 최대 주차 수

# 1학기 날짜 설정
SEMESTER_1_START_MONTH = 3  # 1학기 시작 월
SEMESTER_1_START_DAY = 1  # 1학기 시작 일
SEMESTER_1_END_MONTH = 6  # 1학기 종료 월
SEMESTER_1_END_DAY = 30  # 1학기 종료 일

# 2학기 날짜 설정
SEMESTER_2_START_MONTH = 9  # 2학기 시작 월
SEMESTER_2_START_DAY = 1  # 2학기 시작 일
SEMESTER_2_END_MONTH = 12  # 2학기 종료 월
SEMESTER_2_END_DAY = 31  # 2학기 종료 일


def get_semester_dates(year, semester):
    """
    학기 시작일과 종료일을 반환합니다.
    
    Args:
        year: 연도
        semester: 학기 (1 또는 2)
        
    Returns:
        (start_date, end_date) 튜플
        
    Raises:
        ValueError: 잘못된 학기 값인 경우
    """
    # 1학기인 경우
    if semester == 1:
        start_date = date(year, SEMESTER_1_START_MONTH, SEMESTER_1_START_DAY)
        end_date = date(year, SEMESTER_1_END_MONTH, SEMESTER_1_END_DAY)
    # 2학기인 경우
    elif semester == 2:
        start_date = date(year, SEMESTER_2_START_MONTH, SEMESTER_2_START_DAY)
        end_date = date(year, SEMESTER_2_END_MONTH, SEMESTER_2_END_DAY)
    # 잘못된 학기 값인 경우 에러 발생
    else:
        raise ValueError(f"올바르지 않은 학기 값: {semester}")
    
    return start_date, end_date


# 요일 문자열을 Python weekday 숫자로 매핑 (0: 월요일, 6: 일요일)
WEEKDAY_MAP = {
    'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 
    'FRI': 4, 'SAT': 5, 'SUN': 6
}

# Python weekday 숫자를 요일 문자열로 매핑 (역방향)
WEEKDAY_TO_STR = {
    0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 
    4: 'FRI', 5: 'SAT', 6: 'SUN'
}

# 한글 요일을 영문 요일로 매핑
KOREAN_TO_WEEKDAY = {
    '월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI',
    '토': 'SAT', '일': 'SUN'
}

# 요일 이름 리스트
WEEKDAY_NAMES = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

# 출석 상태 코드를 한글 표시명으로 매핑 (상세 페이지용)
ATTENDANCE_STATUS_MAP = {
    'PRESENT': '출석',
    'LATE': '지각',
    'ABSENT': '결석'
}

# 출석 상태 코드를 한글 표시명으로 매핑 (관리 페이지용)
ATTENDANCE_STATUS_DISPLAY = {
    'PRESENT': '출석완료',
    'LATE': '지각',
    'ABSENT': '결석'
}

