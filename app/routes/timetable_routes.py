from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from mysql.connector import connect, Error
from config import DB_CONFIG
from datetime import timedelta, time

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

@timetable_bp.route('/')
@login_required
def timetable():
    username = session.get('username', '사용자')
    role = session.get('role', 'student')
    user_id = session.get('user_id')

    error = None

    try:
        # ✅ TIME 컬럼이 timedelta로 읽히는 경우를 위한 헬퍼 함수
        def to_time_obj(value):
            if isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return time(hours, minutes)
            return value

        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = ""
                params = (user_id,)

                if role == 'student':
                    # 학생이 수강하는 과목의 스케줄 정보를 가져오기
                    query = """
                        SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                               ss.start_time, ss.end_time, ss.location
                        FROM enrollment e
                        JOIN subject s ON e.subject_id = s.subject_id
                        JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                        LEFT JOIN professor p ON s.professor_id = p.professor_id
                        WHERE e.student_id = %s
                    """
                elif role == 'professor':
                    # 교수가 담당하는 과목의 스케줄 정보를 가져오기
                    query = """
                        SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                               ss.start_time, ss.end_time, ss.location
                        FROM subject s
                        JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                        JOIN professor p ON s.professor_id = p.professor_id
                        WHERE p.professor_id = %s
                    """

                if query:
                    cursor.execute(query, params)
                
                schedules = cursor.fetchall()

                # ✅ 30분 단위 슬롯 (9:00~21:30)
                slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
                timetable_grid = {
                    slot: {day: None for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']}
                    for slot in slots
                }

                # ✅ 요일 매핑
                day_map = {'월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI'}

                for item in schedules:
                    item['day_of_week'] = day_map.get(item['day_of_week'], item['day_of_week'])

                    start_total_seconds = item['start_time'].total_seconds()
                    end_total_seconds = item['end_time'].total_seconds()

                    start_hour = int(start_total_seconds // 3600)
                    start_minute = int((start_total_seconds % 3600) // 60)
                    duration_minutes = (end_total_seconds - start_total_seconds) / 60

                    # ✅ rowspan 30분 단위로 계산
                    rowspan = int(duration_minutes / 30)

                    if (start_hour, start_minute) in timetable_grid:
                        timetable_grid[(start_hour, start_minute)][item['day_of_week']] = {
                            **item, 'rowspan': rowspan
                        }

                    # 다음 슬롯들 skip 처리
                    current_hour, current_minute = start_hour, start_minute
                    for i in range(1, rowspan):
                        current_minute += 30
                        if current_minute >= 60:
                            current_hour += 1
                            current_minute -= 60
                        if (current_hour, current_minute) in timetable_grid:
                            timetable_grid[(current_hour, current_minute)][item['day_of_week']] = 'skip'

    except Error as e:
        error = f"데이터베이스 오류: {e}"
        slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
        timetable_grid = {
            slot: {day: None for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']}
            for slot in slots
        }

    return render_template(
        'time_table.html',
        username=username,
        role=role,
        timetable=timetable_grid,
        error=error,
        days=['MON', 'TUE', 'WED', 'THU', 'FRI']
    )
