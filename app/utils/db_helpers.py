"""
데이터베이스 관련 유틸리티 함수들
"""
from mysql.connector import connect
from config import DB_CONFIG
from datetime import timedelta, time


# DB 연결 설정 상수 (UTF-8 인코딩 설정 포함)
DB_CONNECTION_CONFIG = {
    **DB_CONFIG,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}


def get_db_connection():
    """
    데이터베이스 연결을 반환합니다.
    UTF-8 인코딩 설정이 포함된 연결을 생성합니다.
    
    Returns:
        데이터베이스 연결 객체
    """
    return connect(**DB_CONNECTION_CONFIG)


def to_time(value):
    """
    다양한 형식의 시간 값을 time 객체로 변환합니다.
    
    Args:
        value: timedelta, str, 또는 time 객체
        
    Returns:
        time 객체
    """
    # timedelta 객체인 경우 time 객체로 변환
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return time(hours, minutes)
    # 문자열인 경우 파싱
    elif isinstance(value, str):
        # 길이가 8 이상이면 그대로 사용, 아니면 ':00' 추가
        return time.fromisoformat(value[:8]) if len(value) >= 8 else time.fromisoformat(value + ':00')
    # 이미 time 객체이거나 다른 형식인 경우 그대로 반환
    return value


def format_time_to_str(time_value):
    """
    time 객체를 HH:MM 형식의 문자열로 변환합니다.
    
    Args:
        time_value: time, timedelta, 또는 str 객체
        
    Returns:
        "HH:MM" 형식의 문자열
    """
    # timedelta 객체인 경우 시간과 분 추출
    if isinstance(time_value, timedelta):
        total_seconds = int(time_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    # 문자열인 경우 앞 5자리만 반환 (HH:MM 형식)
    elif isinstance(time_value, str):
        return time_value[:5] if len(time_value) >= 5 else time_value
    # time 객체인 경우 포맷팅
    elif isinstance(time_value, time):
        return time_value.strftime("%H:%M")
    # 기타 형식인 경우 문자열로 변환
    return str(time_value)


def get_student_id_by_number(cursor, student_number):
    """
    학번으로 학생 ID를 조회합니다.
    
    Args:
        cursor: 데이터베이스 커서
        student_number: 학번
        
    Returns:
        student_id (int) 또는 None (학생이 없는 경우)
    """
    cursor.execute("SELECT student_id FROM student WHERE student_number = %s", (student_number,))
    result = cursor.fetchone()
    # 결과가 있으면 student_id 반환, 없으면 None 반환
    return result['student_id'] if result else None


# ============================================================================
# 헬퍼 함수 사용 설명
# ============================================================================
#
# get_db_connection()
#   - 필요성: UTF-8 인코딩 설정이 포함된 DB 연결을 일관되게 생성함. 
#            DB 연결 설정 중앙화로 코드 재사용성 향상 및 인코딩 문제 방지.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance(), check_attendance(), 
#            manage_attendance(), attendance_detail()에서 DB 연결 시 사용됨.
#
# to_time(value)
#   - 필요성: DB에서 가져온 시간 값(timedelta, str, time 등)을 일관된 time 객체로 변환함.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance()에서 
#            start_time과 end_time을 time 객체로 변환할 때 사용됨.
#
# format_time_to_str(time_value)
#   - 필요성: time 객체를 "HH:MM" 형식 문자열로 변환함. 다양한 시간 형식 지원.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance()에서 
#            수업 시간을 템플릿에 전달하기 전 문자열로 변환할 때 사용됨.
#
# get_student_id_by_number(cursor, student_number)
#   - 필요성: 학번으로 학생 ID 조회 로직을 재사용 가능한 함수로 분리함. 코드 중복 방지.
#   - 사용처: app/routes/attendance_routes.py의 show_attendance()에서 
#            학번으로 학생 ID를 조회할 때 사용됨.
#