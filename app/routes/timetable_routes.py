from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from mysql.connector import connect, Error
from config import DB_CONFIG
from datetime import timedelta

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

@timetable_bp.route('/')
@login_required
def timetable():
    username = session.get('username', '사용자')
    role = session.get('role', 'student')
    user_id = session.get('user_id')

    timetable_data = {}
    error = None

    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 학생이 수강하는 과목의 스케줄 정보를 가져오는 쿼리
                query = """
                    SELECT 
                        s.name AS subject_name,
                        p.name AS professor_name,
                        ss.day_of_week,
                        ss.start_time,
                        ss.end_time,
                        ss.location
                    FROM enrollment e
                    JOIN subject s ON e.subject_id = s.subject_id
                    JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                    LEFT JOIN professor p ON s.professor_id = p.professor_id
                    WHERE e.student_id = %s
                """
                cursor.execute(query, (user_id,))
                schedules = cursor.fetchall()

                # 시간표 데이터를 가공하여 그리드 형태로 만듭니다.
                # 30분 단위로 그리드를 생성합니다. 키는 (시간, 분) 튜플을 사용합니다.
                # 예: {(9, 0): {'MON': None, ...}, (9, 30): {'MON': None, ...}}
                slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
                timetable_grid = {slot: {day: None for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']} for slot in slots}

                for item in schedules:
                    # DB의 TIME 타입은 timedelta 객체이므로, total_seconds()로 다루는 것이 가장 안정적입니다.
                    start_total_seconds = item['start_time'].total_seconds()
                    end_total_seconds = item['end_time'].total_seconds()

                    start_hour = int(start_total_seconds // 3600)
                    start_minute = int((start_total_seconds % 3600) // 60)
                    duration_minutes = (end_total_seconds - start_total_seconds) / 60

                    # rowspan을 30분 단위로 계산합니다. (예: 90분 수업 -> 90/30 = 3)
                    rowspan = int(duration_minutes / 30)

                    timetable_grid[(start_hour, start_minute)][item['day_of_week']] = {**item, 'rowspan': rowspan}

                    # rowspan만큼 다음 슬롯들을 'skip'으로 표시합니다.
                    current_hour, current_minute = start_hour, start_minute
                    for i in range(1, rowspan):
                        current_minute += 30
                        if current_minute >= 60:
                            current_hour += 1
                            current_minute = 0
                        if current_hour < 22:
                            timetable_grid[(current_hour, current_minute)][item['day_of_week']] = 'skip'
    except Error as e:
        error = f"데이터베이스 오류: {e}"
        slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
        timetable_grid = {slot: {day: None for day in slots} for slot in slots} # 에러 발생 시 빈 그리드 생성

    return render_template('time_table.html', username=username, role=role, timetable=timetable_grid, error=error, days=['MON', 'TUE', 'WED', 'THU', 'FRI'])