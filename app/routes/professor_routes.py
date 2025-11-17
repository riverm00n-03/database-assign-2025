from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from mysql.connector import connect
from config import DB_CONFIG
from app.utils.auth import login_required

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

from datetime import datetime


@professor_bp.route('/todays_classes', methods=['GET'])
@login_required
def todays_classes():
    """
    교수의 오늘 수업 목록을 표시합니다.
    오늘 요일에 해당하는 교수의 모든 수업을 보여줍니다.
    """
    # 교수가 아닌 경우 접근 제한
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    professor_id = session.get('user_id')
    
    # 오늘 요일 구하기 (0:월요일, 1:화요일, ..., 6:일요일)
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
    today_weekday = day_map[datetime.today().weekday()]

    # 오늘 요일에 해당하는 교수의 모든 수업 목록 조회
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
    """
    오늘 날짜의 수업 세션을 찾거나 생성한 후 출석 관리 페이지로 리다이렉트합니다.
    
    Args:
        schedule_id: 스케줄 ID
    """
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # 오늘 날짜로 이미 생성된 세션이 있는지 확인
                query_select = "SELECT session_id FROM class_session WHERE schedule_id = %s AND class_date = CURDATE()"
                cursor.execute(query_select, (schedule_id,))
                result = cursor.fetchone()

                # 세션이 이미 존재하는 경우
                if result:
                    session_id = result[0]
                # 세션이 없는 경우 새로 생성
                else:
                    query_insert = "INSERT INTO class_session (schedule_id, class_date) VALUES (%s, CURDATE())"
                    cursor.execute(query_insert, (schedule_id,))
                    connection.commit()
                    session_id = cursor.lastrowid

                # 세션 ID가 없으면 에러 발생
                if not session_id:
                    raise Exception("세션 ID를 가져오지 못했습니다.")

                return redirect(url_for('professor.manage_attendance', session_id=session_id))
    except Exception as e:
        flash(f"수업 세션 생성 중 오류 발생: {e}")
        return redirect(url_for('professor.todays_classes'))

@professor_bp.route('/manage_attendance/<int:session_id>', methods=['GET', 'POST'])
@login_required
def manage_attendance(session_id):
    """
    교수의 출석 관리 페이지를 표시하거나 출석 정보를 저장합니다.
    GET 요청 시 수강생 목록과 출석 상태를 보여주고,
    POST 요청 시 출석 정보를 업데이트합니다.
    
    Args:
        session_id: 수업 세션 ID
    """
    # 교수가 아닌 경우 접근 제한
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    # POST 요청인 경우 출석 정보 저장
    if request.method == 'POST':
        try:
            with connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    # 폼에서 전송된 모든 학생의 출석 상태 처리
                    for key, new_status in request.form.items():
                        # status_로 시작하는 키만 처리
                        if key.startswith('status_'):
                            student_id = key.split('_')[1]
                            
                            # 출석 정보를 삽입하거나 이미 존재하면 업데이트
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

        # 저장 후 같은 페이지로 리다이렉트하여 변경된 내용 표시
        return redirect(url_for('professor.manage_attendance', session_id=session_id))

    # GET 요청 처리: 수강생 목록과 출석 상태 조회
    # 특정 수업의 수강생 목록과 각 학생의 현재 출석 상태 조회
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

    # 페이지 상단에 표시할 과목명과 수업 날짜 조회
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

                # 잘못된 session_id인 경우 에러 처리
                if not subject_info:
                    flash("해당 수업 정보를 찾을 수 없습니다.")
                    return redirect(url_for('professor.todays_classes'))

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