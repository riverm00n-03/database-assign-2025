from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from mysql.connector import connect, Error
from config import DB_CONFIG
from datetime import datetime, timedelta, time

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

@professor_bp.route('/today')
@login_required
def todays_classes():
    if session.get('role') != 'professor':
        return "교수만 접근 가능한 페이지입니다.", 403

    professor_id = session.get('user_id')
    username = session.get('username')
    error = None
    classes = []

    # 오늘 요일 구하기 (0:월, 1:화, ..., 6:일)
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
    today_weekday = day_map[datetime.today().weekday()]

    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT
                        s.name AS subject_name,
                        ss.start_time,
                        ss.end_time,
                        ss.location
                    FROM subject s
                    JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                    WHERE s.professor_id = %s AND ss.day_of_week = %s
                    ORDER BY ss.start_time;
                """
                cursor.execute(query, (professor_id, today_weekday))
                classes = cursor.fetchall()

                # 시간 포맷팅 (HH:MM)
                for cls in classes:
                    for key in ['start_time', 'end_time']:
                        if isinstance(cls[key], timedelta):
                            total_seconds = int(cls[key].total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            cls[key] = f"{hours:02d}:{minutes:02d}"

    except Error as e:
        error = f"데이터를 불러오는 중 오류가 발생했습니다: {e}"

    return render_template('todays_classes.html',
                           username=username,
                           role=session.get('role'),
                           classes=classes,
                           error=error)