"""
출석 관련 유틸리티 함수들
"""
from datetime import datetime, timedelta
from app.utils.attendance_test import now
from app.utils.constants import (
    ATTENDANCE_WINDOW_MINUTES,
    ATTENDANCE_STATUS_DISPLAY,
    WEEKDAY_MAP,
    get_semester_dates,
    MAX_WEEKS_PER_SEMESTER
)
from app.utils.db_helpers import format_time_to_str


def get_attendance_window(start_time, class_date):
    """
    출석 가능 시간 범위를 계산합니다.
    수업 시작 시간을 기준으로 전후 일정 시간(기본 10분) 범위를 계산합니다.
    
    Args:
        start_time: 수업 시작 시간 (time 객체)
        class_date: 수업 날짜 (date 객체)
        
    Returns:
        (window_from, window_to, within_window) 튜플
        - window_from: 출석 가능 시작 시간
        - window_to: 출석 가능 종료 시간
        - within_window: 현재 시간이 출석 가능 범위 내인지 여부
    """
    # 수업 시작 datetime 생성
    start_dt = datetime.combine(class_date, start_time)
    # 출석 가능 시작 시간 (수업 시작 전)
    window_from = start_dt - timedelta(minutes=ATTENDANCE_WINDOW_MINUTES)
    # 출석 가능 종료 시간 (수업 시작 후)
    window_to = start_dt + timedelta(minutes=ATTENDANCE_WINDOW_MINUTES)
    # 현재 시간이 출석 가능 범위 내인지 확인
    server_now = datetime.now()
    within_window = window_from <= server_now <= window_to
    
    return window_from, window_to, within_window


def format_attendance_status(status):
    """
    출석 상태 코드를 한글 표시명으로 변환합니다.
    
    Args:
        status: 출석 상태 코드 ('PRESENT', 'LATE', 'ABSENT' 등)
        
    Returns:
        한글 표시명 (기본값: '출석완료')
    """
    return ATTENDANCE_STATUS_DISPLAY.get(status, '출석완료')


def calculate_week_dates(semester_start, schedules):
    """
    각 스케줄의 첫 번째 수업 날짜를 계산합니다.
    학기 시작일부터 각 스케줄의 요일까지의 첫 번째 날짜를 찾습니다.
    
    Args:
        semester_start: 학기 시작일 (date 객체)
        schedules: 스케줄 리스트 (각 스케줄은 day_of_week와 schedule_id를 포함)
        
    Returns:
        {schedule_id: first_date} 딕셔너리
    """
    first_week_dates = {}
    current_date = semester_start
    
    # 각 스케줄에 대해 첫 번째 수업 날짜 계산
    for schedule in schedules:
        day_of_week = WEEKDAY_MAP[schedule['day_of_week']]
        # 학기 시작일부터 해당 요일까지의 일수 계산
        days_ahead = day_of_week - current_date.weekday()
        
        # 음수인 경우 다음 주로 이동
        if days_ahead < 0:
            days_ahead += 7
        # 시작일이 해당 요일인 경우
        elif days_ahead == 0:
            pass
        
        # 첫 번째 수업 날짜 계산
        first_date = current_date + timedelta(days=days_ahead)
        first_week_dates[schedule['schedule_id']] = first_date
    
    return first_week_dates


def build_session_map(sessions):
    """
    세션 데이터를 날짜와 스케줄 ID로 매핑합니다.
    빠른 조회를 위해 딕셔너리 형태로 변환합니다.
    
    Args:
        sessions: 세션 데이터 리스트 (각 세션은 class_date, schedule_id 등을 포함)
        
    Returns:
        {(class_date, schedule_id): session_info} 딕셔너리
    """
    session_map = {}
    # 각 세션을 (날짜, 스케줄 ID) 튜플을 키로 하는 딕셔너리로 변환
    for session_data in sessions:
        session_date = session_data['class_date']
        schedule_id = session_data['schedule_id']
        key = (session_date, schedule_id)
        session_map[key] = {
            'session_id': session_data['session_id'],
            'is_cancelled': session_data['is_cancelled'],
            'start_time': session_data['start_time'],
            'end_time': session_data['end_time'],
            'day_of_week': session_data['day_of_week']
        }
    return session_map


# ============================================================================
# 헬퍼 함수 사용 설명
# ============================================================================
#
# get_attendance_window(start_time, class_date)
#   - 필요성: 수업 시작 시간 기준으로 출석 가능 시간 범위(전후 10분) 계산함. 
#            현재 시간이 범위 내인지 확인함.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance()에서 
#            출석 가능 시간 범위 계산 및 출석 버튼 활성화 여부 결정 시 사용됨.
#
# format_attendance_status(status)
#   - 필요성: 출석 상태 코드('PRESENT', 'LATE', 'ABSENT' 등)를 한글 표시명으로 변환함.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance()에서 
#            출석 상태를 템플릿에 표시하기 전 한글로 변환할 때 사용됨.
#
# calculate_week_dates(semester_start, schedules)
#   - 필요성: 학기 시작일과 스케줄 요일 정보로 각 스케줄의 첫 번째 수업 날짜 계산함.
#   - 사용처: app/routes/attendance_routes.py의 attendance_detail()에서 
#            주차별 출석 기록 생성 시 사용됨.
#
# build_session_map(sessions)
#   - 필요성: 세션 데이터를 (날짜, 스케줄 ID) 키의 딕셔너리로 변환하여 빠른 조회 가능하게 함.
#   - 사용처: app/routes/attendance_routes.py의 attendance_detail()에서 
#            주차별 출석 기록 생성 시 세션 정보 조회에 사용됨.
#