from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from mysql.connector import connect
from config import DB_CONFIG
from app.utils.auth import login_required

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

from datetime import datetime

@professor_bp.route('/todays_classes', methods=['GET'])
@login_required
def todays_classes():
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable')) # 학생의 경우 시간표로 리디렉션

    professor_id = session.get('user_id')
    
    # 오늘 요일 구하기 (0:월, 1:화, ..., 6:일) -> DB ENUM과 매칭
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
    today_weekday = day_map[datetime.today().weekday()]

    # 쿼리: 오늘 '요일'에 해당하는 교수의 모든 수업 목록 조회
    query = """
        SELECT 
            ss.schedule_id,
            s.name AS subject_name,
            TIME_FORMAT(ss.start_time, '%H:%i') AS start_time,
            TIME_FORMAT(ss.end_time, '%H:%i') AS end_time,
            ss.location
        FROM subject_schedule AS ss
        JOIN subject AS s ON ss.subject_id = s.subject_id
        WHERE s.professor_id = %s AND ss.day_of_week = %s
        ORDER BY ss.start_time ASC;
    """
    
    classes = []
    error = None
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (professor_id, today_weekday))
                classes = cursor.fetchall()
    except Exception as e:
        error = f"강의 목록을 불러오는 중 오류가 발생했습니다: {e}"

    return render_template(
        'todays_classes.html', 
        username=session.get('username'), 
        role=session.get('role'),
        classes=classes,
        error=error
    )

@professor_bp.route('/create_session_and_redirect/<int:schedule_id>')
@login_required
def create_session_and_redirect(schedule_id):
    # 오늘 날짜의 class_session을 생성하거나 찾아서 session_id를 가져온 후, manage_attendance로 리디렉션
    query_find_or_create = """
        INSERT INTO class_session (schedule_id, class_date)
        VALUES (%s, CURDATE())
        ON DUPLICATE KEY UPDATE session_id=LAST_INSERT_ID(session_id);
    """
    select_query = "SELECT LAST_INSERT_ID();"
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_find_or_create, (schedule_id,))
                cursor.execute(select_query)
                session_id = cursor.fetchone()[0]
                return redirect(url_for('professor.manage_attendance', session_id=session_id))
    except Exception as e:
        flash(f"수업 세션 생성 중 오류 발생: {e}")
        return redirect(url_for('professor.todays_classes'))

@professor_bp.route('/manage_attendance/<int:session_id>', methods=['GET'])
@login_required
def manage_attendance(session_id):
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    # 쿼리: 특정 수업(session)의 수강생 목록과 각 학생의 현재 출결 상태를 조회
    student_query = """
        SELECT
            st.student_id,
            st.name,
            st.student_number,
            st.student_major,
            chk.status
        FROM enrollment AS en
        JOIN student AS st ON en.student_id = st.student_id
        JOIN class_session AS cs ON en.subject_id = (SELECT subject_id FROM subject_schedule WHERE schedule_id = cs.schedule_id)
        LEFT JOIN checkin AS chk ON cs.session_id = chk.session_id AND en.student_id = chk.student_id
        WHERE cs.session_id = %s
        ORDER BY st.student_number ASC;
    """

    # 쿼리: 페이지 상단에 표시할 과목명과 수업 날짜 조회
    subject_query = """
        SELECT
            s.name AS subject_name,
            DATE_FORMAT(cs.class_date, '%Y년 %m월 %d일') AS class_date
        FROM class_session AS cs
        JOIN subject_schedule AS ss ON cs.schedule_id = ss.schedule_id
        JOIN subject AS s ON ss.subject_id = s.subject_id
        WHERE cs.session_id = %s
    """

    students = []
    subject_info = {}

    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 학생 목록 조회
                cursor.execute(student_query, (session_id,))
                students = cursor.fetchall()
                # 과목 정보 조회
                cursor.execute(subject_query, (session_id,))
                subject_info = cursor.fetchone()

    except Exception as e:
        flash(f"출석 정보를 불러오는 중 오류가 발생했습니다: {e}")
        return redirect(url_for('professor.todays_classes'))

    return render_template(
        'manage_attendance.html',
        role=session.get('role'),
        session_id=session_id,
        students=students,
        subject_name=subject_info.get('subject_name'),
        class_date=subject_info.get('class_date')
    )