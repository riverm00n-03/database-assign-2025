from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from mysql.connector import connect
from config import DB_CONFIG
from app.utils.auth import login_required

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

from datetime import datetime, date, timedelta

@professor_bp.route('/attendance', methods=['GET'], endpoint='manage_subjects') # 엔드포인트 이름을 명시적으로 지정
@login_required
def manage_subjects():
    """교수가 담당하는 과목 목록을 보여주는 페이지"""
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    professor_id = session.get('user_id')

    # 교수가 담당하는 과목 목록 조회
    query = "SELECT subject_id, name FROM subject WHERE professor_id = %s ORDER BY name ASC"
    subjects = []
    error = None
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (professor_id,))
                subjects = cursor.fetchall()
    except Exception as e:
        error = f"과목 목록을 불러오는 중 오류가 발생했습니다: {e}"

    return render_template(
        'professor_subjects.html',
        username=session.get('username'), 
        role=session.get('role'),
        subjects=subjects,
        error=error
    )

@professor_bp.route('/attendance/<int:subject_id>')
@login_required
def subject_attendance_weeks(subject_id):
    """특정 과목의 주차별 출석 관리 목록을 보여주는 페이지"""
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    # 학기 시작일 (예: 2025년 3월 1일) - 필요시 설정 변경
    semester_start_date = date(2025, 3, 1)
    today = date.today()
    
    # 현재 주차 계산
    days_since_start = (today - semester_start_date).days
    current_week = (days_since_start // 7) + 1

    weeks_data = []
    subject_name = ""
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 과목 이름 조회
                cursor.execute("SELECT name FROM subject WHERE subject_id = %s", (subject_id,))
                subject_result = cursor.fetchone()
                if subject_result:
                    subject_name = subject_result['name']

                # 해당 과목의 모든 수업 스케줄 조회
                query = """
                    SELECT schedule_id, day_of_week, start_time 
                    FROM subject_schedule 
                    WHERE subject_id = %s 
                    ORDER BY FIELD(day_of_week, 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), start_time
                """
                cursor.execute(query, (subject_id,))
                schedules = cursor.fetchall()

                day_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}

                # 1주차부터 16주차까지 생성
                for week_num in range(1, 17):
                    week_start_date = semester_start_date + timedelta(weeks=week_num - 1)
                    classes_in_week = []
                    for schedule in schedules:
                        day_offset = day_map.get(schedule['day_of_week'], 0)
                        class_date = week_start_date + timedelta(days=day_offset - week_start_date.weekday())
                        classes_in_week.append({
                            'schedule_id': schedule['schedule_id'],
                            'class_date': class_date.strftime('%Y-%m-%d'),
                            'class_date_formatted': class_date.strftime('%m월 %d일') + f" ({schedule['day_of_week']})"
                        })
                    weeks_data.append({'week_number': week_num, 'classes': classes_in_week})

    except Exception as e:
        flash(f"주차별 수업 정보를 불러오는 중 오류가 발생했습니다: {e}")

    return render_template(
        'subject_attendance_weeks.html',
        username=session.get('username'),
        role=session.get('role'),
        subject_name=subject_name,
        weeks_data=weeks_data,
        current_week=current_week
    )

@professor_bp.route('/create_session_and_redirect/<int:schedule_id>/<string:class_date_str>')
@login_required
def create_session_and_redirect(schedule_id, class_date_str):
    """
    오늘 날짜의 수업 세션(class_session)을 찾거나 생성한 후,
    해당 세션 ID를 가지고 출석 관리 페이지로 리디렉션합니다.
    """
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # 1. 특정 날짜로 이미 생성된 세션이 있는지 확인
                query_select = "SELECT session_id FROM class_session WHERE schedule_id = %s AND class_date = %s"
                cursor.execute(query_select, (schedule_id, class_date_str))
                result = cursor.fetchone()

                if result:
                    # 2a. 세션이 이미 존재하면 해당 ID 사용
                    session_id = result[0]
                else:
                    # 2b. 세션이 없으면 특정 날짜로 새로 생성
                    query_insert = "INSERT INTO class_session (schedule_id, class_date) VALUES (%s, %s)"
                    cursor.execute(query_insert, (schedule_id, class_date_str))
                    connection.commit()  # INSERT 실행 후에는 commit 필수
                    session_id = cursor.lastrowid # 방금 삽입된 행의 ID 가져오기

                if not session_id:
                    raise Exception("세션 ID를 가져오지 못했습니다.")

                return redirect(url_for('professor.manage_attendance', session_id=session_id))
    except Exception as e:
        flash(f"수업 세션 생성 중 오류 발생: {e}", "error")
        return redirect(request.referrer or url_for('professor.manage_subjects'))

@professor_bp.route('/manage_attendance/<int:session_id>', methods=['GET', 'POST'])
@login_required
def manage_attendance(session_id):
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    if request.method == 'POST':
        try:
            with connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    # 폼에서 전송된 모든 학생의 상태 데이터를 가져옵니다.
                    for key, new_status in request.form.items():
                        if key.startswith('status_'):
                            student_id = key.split('_')[1]
                            
                            # 출결 정보를 삽입하거나, 이미 존재하면 업데이트합니다.
                            upsert_query = """
                                INSERT INTO checkin (session_id, student_id, status)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE status = VALUES(status);
                            """
                            cursor.execute(upsert_query, (session_id, student_id, new_status))
                    
                    connection.commit()
                    flash("출결 상태가 성공적으로 저장되었습니다.")

        except Exception as e:
            flash(f"출결 정보 저장 중 오류가 발생했습니다: {e}")

        # 저장 후, 같은 페이지로 다시 리디렉션하여 변경된 내용을 보여줍니다.
        return redirect(url_for('professor.manage_attendance', session_id=session_id))

    # --- 이하 GET 요청 처리 로직 ---

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

                # subject_info가 None일 경우 (잘못된 session_id 등) 처리
                if not subject_info:
                    flash("해당 수업 정보를 찾을 수 없습니다.")
                    return redirect(url_for('professor.manage_subjects'))

    except Exception as e:
        flash(f"출석 정보를 불러오는 중 오류가 발생했습니다: {e}")
        return redirect(url_for('professor.manage_subjects'))

    return render_template(
        'manage_attendance.html',
        role=session.get('role'),
        session_id=session_id,
        students=students,
        subject_name=subject_info.get('subject_name'),
        class_date=subject_info.get('class_date')
    )