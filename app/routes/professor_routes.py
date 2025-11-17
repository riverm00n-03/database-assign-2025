from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from mysql.connector import connect, Error
from config import DB_CONFIG
from app.utils.auth import login_required
from datetime import datetime, timedelta, time

# defaultdict와 같은 복잡한 라이브러리 대신 기본 자료구조 사용
# from collections import defaultdict

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')


# --- 새로운 출석 관리 기능 ---

@professor_bp.route('/attendance')
@login_required
def lecture_list():
    """출석 관리 메인 페이지: 교수가 담당하는 과목 목록을 보여줌 (단순화된 버전)"""
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    professor_id = session.get('user_id')
    subjects = []
    
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 교수가 담당하는 과목 목록을 가져오는 단순한 쿼리
                query = """
                    SELECT subject_id, name
                    FROM subject
                    WHERE professor_id = %s
                    ORDER BY name;
                """
                cursor.execute(query, (professor_id,))
                subjects = cursor.fetchall()

    except Error as e:
        flash(f"과목 목록을 불러오는 중 오류가 발생했습니다: {e}")
        return redirect(url_for('auth.login'))

    return render_template('professor/lecture_list.html', subjects=subjects, role=session.get('role'))

@professor_bp.route('/subject/<int:subject_id>/sessions')
@login_required
def list_subject_sessions(subject_id):
    """특정 과목의 학기 전체 수업 목록을 보여줌 (단순화된 버전)"""

    # --- 1. 기본 정보 설정 ---
    SEMESTER_START = datetime(2025, 3, 1).date()
    SEMESTER_END = datetime(2025, 6, 20).date()
    today = datetime.now().date()
    subject_name = ""
    all_sessions = []

    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # --- 2. DB에서 필요한 정보 가져오기 ---
                # 과목 이름 조회
                cursor.execute("SELECT name FROM subject WHERE subject_id = %s", (subject_id,))
                subject_result = cursor.fetchone()
                if not subject_result:
                    flash("과목 정보를 찾을 수 없습니다.", "error")
                    return redirect(url_for('professor.lecture_list'))
                subject_name = subject_result['name']

                # 이 과목의 모든 정규 스케줄(요일/시간) 조회
                schedules_query = "SELECT * FROM subject_schedule WHERE subject_id = %s"
                cursor.execute(schedules_query, (subject_id,))
                schedules = cursor.fetchall()

                # DB에 이미 기록된 모든 수업 세션(휴강 포함) 조회
                db_sessions_query = """
                    SELECT
                        cs.session_id, cs.class_date, cs.is_cancelled, ss.schedule_id
                    FROM class_session cs
                    JOIN subject_schedule ss ON cs.schedule_id = ss.schedule_id
                    WHERE ss.subject_id = %s;
                """
                cursor.execute(db_sessions_query, (subject_id,))
                db_sessions = cursor.fetchall()
                db_sessions_map = {(s['class_date'], s['schedule_id']): s for s in db_sessions}

                # --- 3. 학기 전체 수업 목록 생성 ---
                day_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
                current_date = SEMESTER_START
                while current_date <= SEMESTER_END:
                    for schedule in schedules:
                        # 오늘 날짜의 요일과 스케줄의 요일이 일치하는지 확인
                        if current_date.weekday() == day_map.get(schedule['day_of_week'].upper()):
                            session_info = {}
                            session_key = (current_date, schedule['schedule_id'])
                            if session_key in db_sessions_map:
                                # DB에 기록이 있으면 그 정보를 사용
                                session_info.update(db_sessions_map[session_key])
                            else:
                                # DB에 기록이 없으면 '예정된' 수업으로 간주하고 새로 만듦
                                session_info.update({
                                    'session_id': None,
                                    'class_date': current_date,
                                    'is_cancelled': False,
                                    'schedule_id': schedule['schedule_id'],
                                })
                            # 공통 정보 추가
                            session_info['day_of_week'] = schedule['day_of_week']
                            session_info['start_time'] = (datetime.min + schedule['start_time']).strftime('%H:%M')
                            session_info['end_time'] = (datetime.min + schedule['end_time']).strftime('%H:%M')
                            all_sessions.append(session_info)
                    current_date += timedelta(days=1)

                # --- 4. '다음 수업' 찾아서 표시하기 ---
                next_class_found = False
                # 날짜 오름차순으로 정렬 후 '다음 수업' 플래그 설정
                all_sessions.sort(key=lambda x: x['class_date'])
                for session in all_sessions:
                    if not next_class_found and session['class_date'] >= today:
                        session['is_next_class'] = True
                        next_class_found = True
                    else:
                        session['is_next_class'] = False

    except Error as e:
        flash(f"수업 세션 목록을 불러오는 중 오류가 발생했습니다: {e}")
        return redirect(url_for('professor.lecture_list'))

    return render_template('professor/subject_sessions.html',
                           sessions_info=all_sessions,
                           subject_name=subject_name,
                           subject_id=subject_id,
                           role=session.get('role'),
                           today=today)

@professor_bp.route('/cancel_session/<int:schedule_id>/<class_date>')
@login_required
def cancel_session(schedule_id, class_date):
    """수업을 휴강 처리하는 라우트"""
    subject_id = None
    class_date_obj = datetime.strptime(class_date, '%Y-%m-%d').date()
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # subject_id를 먼저 조회 (리디렉션을 위해)
                cursor.execute("SELECT subject_id FROM subject_schedule WHERE schedule_id = %s", (schedule_id,))
                result = cursor.fetchone()
                if result:
                    subject_id = result['subject_id']

                cursor.execute("SELECT session_id FROM class_session WHERE schedule_id = %s AND class_date = %s", (schedule_id, class_date_obj))
                session_result = cursor.fetchone()

                if session_result:
                    cursor.execute("UPDATE class_session SET is_cancelled = TRUE WHERE session_id = %s", (session_result['session_id'],))
                else:
                    cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, TRUE)", (schedule_id, class_date_obj))
                
                connection.commit()
                flash(f"{class_date} 수업이 휴강 처리되었습니다.")
    except Error as e:
        flash(f"휴강 처리 중 오류가 발생했습니다: {e}")

    if subject_id:
        return redirect(url_for('professor.list_subject_sessions', subject_id=subject_id))
    else:
        flash("과목 정보를 찾지 못해 기본 목록으로 돌아갑니다.")
        return redirect(url_for('professor.lecture_list'))


@professor_bp.route('/uncancel_session/<int:session_id>')
@login_required
def uncancel_session(session_id):
    """휴강 처리를 취소하는 라우트"""
    subject_id = None
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT ss.subject_id
                    FROM class_session cs
                    JOIN subject_schedule ss ON cs.schedule_id = ss.schedule_id
                    WHERE cs.session_id = %s
                """, (session_id,))
                result = cursor.fetchone()
                if result:
                    subject_id = result['subject_id']

                cursor.execute("UPDATE class_session SET is_cancelled = FALSE WHERE session_id = %s", (session_id,))
                connection.commit()
                flash("휴강 처리가 취소되었습니다.")
    except Error as e:
        flash(f"휴강 취소 중 오류가 발생했습니다: {e}")

    return redirect(url_for('professor.list_subject_sessions', subject_id=subject_id) if subject_id else url_for('professor.lecture_list'))

@professor_bp.route('/manage_attendance/<int:session_id>', methods=['GET', 'POST'])
@login_required
def manage_attendance(session_id):
    """출결 관리 페이지"""
    if session.get('role') != 'professor':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('timetable.timetable'))

    if request.method == 'POST':
        try:
            with connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    for key, new_status in request.form.items():
                        if key.startswith('status_'):
                            student_id = key.split('_')[1]
                            upsert_query = """
                                INSERT INTO checkin (session_id, student_id, status)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE status = VALUES(status);
                            """
                            cursor.execute(upsert_query, (session_id, student_id, new_status))
                    
                    connection.commit()
                    flash("출결 상태가 성공적으로 저장되었습니다.")

        except Error as e:
            flash(f"출결 정보 저장 중 오류가 발생했습니다: {e}")

        return redirect(url_for('professor.manage_attendance', session_id=session_id))

    student_query = """
        SELECT
            st.student_id, st.name, st.student_number, st.student_major,
            COALESCE(chk.status, '미처리') AS status
        FROM
            enrollment en
            JOIN student st ON en.student_id = st.student_id
            JOIN subject_schedule ss ON en.subject_id = ss.subject_id
            JOIN class_session cs ON ss.schedule_id = cs.schedule_id
            LEFT JOIN checkin chk ON cs.session_id = chk.session_id AND st.student_id = chk.student_id
        WHERE
            cs.session_id = %s
        GROUP BY st.student_id, st.name, st.student_number, st.student_major, chk.status
        ORDER BY st.student_number;
    """

    subject_query = """
        SELECT
            s.subject_id,
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
                cursor.execute(student_query, (session_id,))
                students = cursor.fetchall()
                
                cursor.execute(subject_query, (session_id,))
                subject_info = cursor.fetchone()

                if not subject_info:
                    flash("해당 수업 정보를 찾을 수 없습니다.")
                    return redirect(url_for('professor.lecture_list'))

    except Error as e:
        flash(f"출석 정보를 불러오는 중 오류가 발생했습니다: {e}")
        return redirect(url_for('professor.lecture_list'))

    return render_template(
        'professor/manage_attendance.html',
        role=session.get('role'),
        session_id=session_id,
        students=students,
        subject_name=subject_info.get('subject_name'),
        class_date=subject_info.get('class_date'),
        subject_id=subject_info.get('subject_id')
    )