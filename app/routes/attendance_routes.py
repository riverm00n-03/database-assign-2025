from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from app.utils.auth import login_required
from mysql.connector import connect
from config import DB_CONFIG
from datetime import datetime, timedelta, time

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def show_attendance():
    username = session.get('username', '학생')
    role = session.get('role', 'student')

    # ✅ 서버 시간 (한국 기준)
    server_now = datetime.now()

    # ✅ 평일 매핑 (월~금)
    weekday_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}
    today_index = server_now.weekday()

    # ✅ 주말일 경우 수업 없음
    if today_index > 4:
        return render_template(
            'attendance_check.html',
            username=username,
            role=role,
            server_now_iso=server_now.isoformat(),
            server_now_fmt=server_now.strftime("%Y-%m-%d %H:%M:%S"),
            today_classes=[],
            error="오늘은 주말입니다. 수업이 없습니다."
        )

    today_weekday = weekday_map[today_index]
    today_classes = []

    try:
        with connect(**DB_CONFIG, charset='utf8mb4', collation='utf8mb4_general_ci') as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT ss.schedule_id, s.name AS subject_name, p.name AS professor_name,
                           ss.location, ss.start_time, ss.end_time
                    FROM subject_schedule ss
                    JOIN subject s ON ss.subject_id = s.subject_id
                    LEFT JOIN professor p ON s.professor_id = p.professor_id
                    WHERE UPPER(ss.day_of_week) = %s
                    ORDER BY ss.start_time
                """, (today_weekday.upper(),))
                rows = cursor.fetchall()

                for row in rows:
                    # ✅ TIME 컬럼이 timedelta로 읽히는 경우 보정
                    def to_time(value):
                        if isinstance(value, timedelta):
                            total_seconds = int(value.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            return time(hours, minutes)
                        elif isinstance(value, str):
                            return datetime.strptime(value, "%H:%M:%S").time()
                        return value

                    row['start_time'] = to_time(row['start_time'])
                    row['end_time'] = to_time(row['end_time'])

                    # ✅ 출석 가능 범위: 시작 10분 전 ~ 10분 후
                    start_dt = datetime.combine(server_now.date(), row['start_time'])
                    window_from = start_dt - timedelta(minutes=10)
                    window_to = start_dt + timedelta(minutes=10)
                    within_window = window_from <= server_now <= window_to

                    today_classes.append({
                        'schedule_id': row['schedule_id'],
                        'subject_name': row['subject_name'],
                        'professor_name': row['professor_name'],
                        'location': row['location'],
                        'start_time_str': row['start_time'].strftime("%H:%M"),
                        'end_time_str': row['end_time'].strftime("%H:%M"),
                        'window_from_str': window_from.strftime("%H:%M"),
                        'window_to_str': window_to.strftime("%H:%M"),
                        'window_open': within_window,
                        'status': '미출석'
                    })

    except Exception as e:
        flash(f"데이터베이스 오류: {e}", "error")

    return render_template(
        'attendance_check.html',
        username=username,
        role=role,
        server_now_iso=server_now.isoformat(),
        server_now_fmt=server_now.strftime("%Y-%m-%d %H:%M:%S"),
        today_classes=today_classes
    )


# ✅ 출석 버튼 누를 때 호출되는 POST 엔드포인트
@attendance_bp.route('/check', methods=['POST'])
@login_required
def check_attendance():
    schedule_id = request.form.get('schedule_id')
    username = session.get('username', '학생')

    try:
        with connect(**DB_CONFIG, charset='utf8mb4', collation='utf8mb4_general_ci') as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO attendance (student_name, schedule_id, check_time)
                    VALUES (%s, %s, NOW())
                """, (username, schedule_id))
                conn.commit()
        flash("출석이 완료되었습니다!", "success")
    except Exception as e:
        flash(f"출석 처리 중 오류가 발생했습니다: {e}", "error")

    return redirect(url_for('attendance.show_attendance'))
