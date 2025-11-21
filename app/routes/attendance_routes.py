from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from app.utils.auth import login_required
from app.utils.db_helpers import get_db_connection, to_time, format_time_to_str, get_student_id_by_number
from app.utils.attendance_test import now #테스트 추가
from app.utils.constants import (
    ATTENDANCE_WINDOW_MINUTES,
    ATTENDANCE_STATUS_DISPLAY,
    WEEKDAY_MAP,
    get_semester_dates,
    MAX_WEEKS_PER_SEMESTER
)
from app.utils.attendance_helpers import (
    get_attendance_window,
    format_attendance_status,
    calculate_week_dates,
    build_session_map
)
from datetime import datetime, timedelta

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def show_attendance():
    """
    오늘의 출석 체크 페이지를 표시합니다.
    학생이 오늘 수강하는 수업 목록과 출석 가능 여부를 보여줍니다.
    """
    username = session.get('username', '학생')
    role = session.get('role', 'student')
    student_number = session.get('student_number')

    server_now = datetime.now() # 테스트 원래 datetime.now()
    # 오늘 요일 인덱스 가져오기 (0: 월요일, 6: 일요일)
    today_index = server_now.weekday()

    # 주말일 경우 수업이 없으므로 빈 페이지 반환
    if today_index > 4:
        return render_template(
            'students/attendance_check.html',
            username=username,
            role=role,
            server_now_iso=server_now.isoformat(),
            server_now_fmt=server_now.strftime("%Y-%m-%d %H:%M:%S"),
            today_classes=[],
            error="오늘은 주말입니다. 수업이 없습니다."
        )

    # 요일 인덱스를 DB 형식으로 변환
    weekday_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}
    today_weekday = weekday_map[today_index]
    today_classes = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 학생 역할인 경우에만 학생 ID 조회
                student_id = None
                if role == 'student':
                    student_id = get_student_id_by_number(cursor, student_number)
                    # 학생 정보가 없으면 로그인 페이지로 리다이렉트
                    if not student_id:
                        flash("학생 정보를 찾을 수 없습니다.", "error")
                        return redirect(url_for('auth.login'))

                # 오늘 수업 스케줄 조회
                cursor.execute("""
                    SELECT ss.schedule_id, s.name AS subject_name, p.name AS professor_name,
                           ss.location, ss.start_time, ss.end_time, s.subject_id
                    FROM subject_schedule ss
                    JOIN subject s ON ss.subject_id = s.subject_id
                    LEFT JOIN professor p ON s.professor_id = p.professor_id
                    JOIN enrollment e ON e.subject_id = s.subject_id   -- ★ 필수
                    WHERE UPPER(ss.day_of_week) = %s
                      AND e.student_id = %s                            -- ★ 필수
                    ORDER BY ss.start_time

                """, (today_weekday.upper(),student_id))
                rows = cursor.fetchall()

                # 각 수업에 대해 출석 정보 처리
                for row in rows:
                    # DB에서 가져온 시간 값을 time 객체로 변환
                    row['start_time'] = to_time(row['start_time'])
                    row['end_time'] = to_time(row['end_time'])

                    # 오늘 날짜의 수업 세션이 없으면 생성
                    session_id = _get_or_create_session(cursor, conn, row['schedule_id'], server_now.date())

                    # 출석 가능 시간 범위 계산 (수업 시작 전후 10분)
                    window_from, window_to, within_window = get_attendance_window(
                        row['start_time'], server_now.date()
                    )

                    # 학생의 출석 상태 확인
                    current_status = '미출석'
                    if student_id:
                        checkin_result = _get_checkin_status(cursor, session_id, student_id)
                        # 출석 기록이 있으면 상태 표시명으로 변환
                        if checkin_result:
                            current_status = format_attendance_status(checkin_result['status'])

                    today_classes.append({
                        'schedule_id': row['schedule_id'],
                        'session_id': session_id,
                        'subject_id': row['subject_id'],
                        'subject_name': row['subject_name'],
                        'professor_name': row['professor_name'],
                        'location': row['location'],
                        'start_time_str': format_time_to_str(row['start_time']),
                        'end_time_str': format_time_to_str(row['end_time']),
                        'window_from_str': window_from.strftime("%H:%M"),
                        'window_to_str': window_to.strftime("%H:%M"),
                        'window_open': within_window,
                        'status': current_status
                    })

    except Exception as e:
        # 사용자에게는 일반적인 에러 메시지만 표시
        flash(f"데이터베이스 오류가 발생했습니다.", "error")
        # 개발 환경에서만 상세 에러 로그 출력
        import os
        if os.getenv('FLASK_ENV') == 'development':
            print(f"Error in show_attendance: {e}")

    return render_template(
        'students/attendance_check.html',
        username=username,
        role=role,
        server_now_iso=server_now.isoformat(),
        server_now_fmt=server_now.strftime("%Y-%m-%d %H:%M:%S"),
        today_classes=today_classes
    )


def _get_or_create_session(cursor, conn, schedule_id, class_date):
    """
    특정 날짜의 수업 세션을 조회하거나 없으면 생성합니다.
    
    Args:
        cursor: 데이터베이스 커서
        conn: 데이터베이스 연결
        schedule_id: 스케줄 ID
        class_date: 수업 날짜
        
    Returns:
        session_id: 수업 세션 ID
    """
    # 기존 세션 조회
    cursor.execute(
        "SELECT session_id FROM class_session WHERE schedule_id = %s AND class_date = %s",
        (schedule_id, class_date)
    )
    session_result = cursor.fetchone()

    # 세션이 존재하면 기존 ID 반환
    if session_result:
        return session_result['session_id']
    # 세션이 없으면 새로 생성
    else:
        cursor.execute(
            "INSERT INTO class_session (schedule_id, class_date) VALUES (%s, %s)",
            (schedule_id, class_date)
        )
        conn.commit()
        return cursor.lastrowid


def _get_checkin_status(cursor, session_id, student_id):
    """
    특정 학생의 특정 세션에 대한 출석 상태를 조회합니다.
    
    Args:
        cursor: 데이터베이스 커서
        session_id: 수업 세션 ID
        student_id: 학생 ID
        
    Returns:
        출석 기록 딕셔너리 또는 None
    """
    cursor.execute(
        "SELECT status FROM checkin WHERE session_id = %s AND student_id = %s",
        (session_id, student_id)
    )
    return cursor.fetchone()


@attendance_bp.route('/check', methods=['POST'])
@login_required
def check_attendance():
    """
    출석 체크 버튼을 눌렀을 때 호출되는 POST 엔드포인트입니다.
    학생의 출석을 기록합니다.
    """
    schedule_id = request.form.get('schedule_id')
    student_number = session.get('student_number')

    # 세션에 학번이 없으면 로그인 페이지로 리다이렉트
    if not student_number:
        flash("로그인 정보가 없습니다.", "error")
        return redirect(url_for('auth.login'))

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 학생 ID 조회
                cursor.execute("SELECT student_id FROM student WHERE student_number = %s", (student_number,))
                student_result = cursor.fetchone()
                # 학생 정보가 없으면 에러 처리
                if not student_result:
                    flash("학생 정보를 찾을 수 없습니다.", "error")
                    return redirect(url_for('attendance.show_attendance'))
                student_id = student_result['student_id']

                # 오늘 날짜의 수업 세션 ID 조회
                server_now = datetime.now()
                cursor.execute(
                    "SELECT session_id FROM class_session WHERE schedule_id = %s AND class_date = %s",
                    (schedule_id, server_now.date())
                )
                session_result = cursor.fetchone()
                # 세션이 없으면 에러 처리
                if not session_result:
                    flash("해당 수업 세션을 찾을 수 없습니다. 관리자에게 문의하세요.", "error")
                    return redirect(url_for('attendance.show_attendance'))
                session_id = session_result['session_id']

                # 중복 출석 체크 방지
                cursor.execute(
                    "SELECT checkin_id FROM checkin WHERE session_id = %s AND student_id = %s",
                    (session_id, student_id)
                )
                # 이미 출석 기록이 있으면 처리하지 않음
                if cursor.fetchone():
                    flash("이미 출석 처리되었습니다.", "info")
                    return redirect(url_for('attendance.show_attendance'))

                # 출석 기록 삽입
                cursor.execute("""
                    INSERT INTO checkin (session_id, student_id, check_time, status)
                    VALUES (%s, %s, NOW(), 'PRESENT')
                """, (session_id, student_id))
                conn.commit()
        flash("출석이 완료되었습니다!", "success")
    except Exception as e:
        flash(f"출석 처리 중 오류가 발생했습니다: {e}", "error")

    return redirect(url_for('attendance.show_attendance'))


def calculate_attendance_status(total_sessions, present_count, late_count, absent_count):
    """
    출석률과 상태(안전/주의/위험)를 계산합니다.
    지각 3회는 결석 1회로 처리합니다.
    
    Args:
        total_sessions: 총 수업 세션 수
        present_count: 출석 횟수
        late_count: 지각 횟수
        absent_count: 결석 횟수
        
    Returns:
        (attendance_percentage, status_text, status_color) 튜플
    """
    # 수업이 없는 경우 100% 출석으로 간주
    if total_sessions == 0:
        return 100, '안전', 'green'

    # 지각 3회를 결석 1회로 환산하여 유효 결석 수 계산
    effective_absent_count = absent_count + (late_count // 3)
    effective_present_count = total_sessions - effective_absent_count

    # 음수 방지 (로직상 발생하지 않아야 하지만 안전장치)
    if effective_present_count < 0:
        effective_present_count = 0

    # 출석률 계산
    attendance_percentage = (effective_present_count / total_sessions) * 100

    # 출석률에 따른 상태 결정
    status_text = '안전'
    status_color = 'green'
    # 출석률 80% 미만: 위험
    if attendance_percentage < 80:
        status_text = '위험'
        status_color = 'red'
    # 출석률 80% 이상 90% 미만: 주의
    elif 80 <= attendance_percentage < 90:
        status_text = '주의'
        status_color = 'orange'
    
    return attendance_percentage, status_text, status_color


@attendance_bp.route('/manage')
@login_required
def manage_attendance_students():
    """
    학생의 출석 관리 페이지를 표시합니다.
    수강 중인 모든 과목의 출석 현황을 보여줍니다.
    """
    username = session.get('username', '학생')
    role = session.get('role', 'student')
    student_number = session.get('student_number')

    # 학생이 아닌 경우 접근 제한
    if role != 'student':
        flash("학생만 출석 관리를 이용할 수 있습니다.", "error")
        return redirect(url_for('main.index'))

    # 세션에 학번이 없으면 로그인 페이지로 리다이렉트
    if not student_number:
        flash("로그인 정보가 없습니다.", "error")
        return redirect(url_for('auth.login'))

    enrolled_subjects_data = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 학생 ID 조회
                cursor.execute("SELECT student_id FROM student WHERE student_number = %s", (student_number,))
                student_result = cursor.fetchone()
                # 학생 정보가 없으면 로그인 페이지로 리다이렉트
                if not student_result:
                    flash("학생 정보를 찾을 수 없습니다.", "error")
                    return redirect(url_for('auth.login'))
                student_id = student_result['student_id']

                # 학생이 수강하는 모든 과목을 가져온다.
                cursor.execute("""
                    SELECT s.subject_id, s.name AS subject_name, p.name AS professor_name
                    FROM enrollment e
                    JOIN subject s ON e.subject_id = s.subject_id
                    LEFT JOIN professor p ON s.professor_id = p.professor_id
                    WHERE e.student_id = %s
                """, (student_id,))
                enrolled_subjects = cursor.fetchall()

                # 각 수강 과목에 대해 출석 통계 계산
                for subject in enrolled_subjects:
                    subject_id = subject['subject_id']
                    
                    # 해당 과목의 총 수업 세션 수 조회 (휴강 제외)
                    cursor.execute("""
                        SELECT COUNT(DISTINCT cs.session_id) AS total_sessions
                        FROM class_session cs
                        JOIN subject_schedule ss ON cs.schedule_id = ss.schedule_id
                        WHERE ss.subject_id = %s AND cs.is_cancelled = FALSE
                    """, (subject_id,))
                    total_sessions_result = cursor.fetchone()
                    # 결과가 없으면 0으로 설정
                    total_sessions = total_sessions_result['total_sessions'] if total_sessions_result else 0

                    # 해당 과목에 대한 학생의 출석 통계 조회
                    cursor.execute("""
                        SELECT
                            SUM(CASE WHEN c.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_count,
                            SUM(CASE WHEN c.status = 'LATE' THEN 1 ELSE 0 END) AS late_count,
                            SUM(CASE WHEN c.status = 'ABSENT' THEN 1 ELSE 0 END) AS absent_count
                        FROM checkin c
                        JOIN class_session cs ON c.session_id = cs.session_id
                        JOIN subject_schedule ss ON cs.schedule_id = ss.schedule_id
                        WHERE c.student_id = %s AND ss.subject_id = %s AND cs.is_cancelled = FALSE
                    """, (student_id, subject_id))
                    checkin_counts = cursor.fetchone()

                    # NULL 값 처리: 결과가 없거나 값이 NULL이면 0으로 설정
                    present_count = checkin_counts['present_count'] if checkin_counts and checkin_counts['present_count'] is not None else 0
                    late_count = checkin_counts['late_count'] if checkin_counts and checkin_counts['late_count'] is not None else 0
                    absent_count = checkin_counts['absent_count'] if checkin_counts and checkin_counts['absent_count'] is not None else 0

                    attendance_percentage, status_text, status_color = calculate_attendance_status(
                        total_sessions, present_count, late_count, absent_count
                    )

                    enrolled_subjects_data.append({
                        'subject_id': subject_id,
                        'subject_name': subject['subject_name'],
                        'professor_name': subject['professor_name'],
                        'total_sessions': total_sessions,
                        'present_count': present_count,
                        'late_count': late_count,
                        'absent_count': absent_count,
                        'attendance_percentage': round(attendance_percentage, 2),
                        'status_text': status_text,
                        'status_color': status_color
                    })

    except Exception as e:
        flash(f"데이터베이스 오류: {e}", "error")
        # 개발 환경에서만 상세 에러 로그 출력
        import os
        if os.getenv('FLASK_ENV') == 'development':
            print(f"Error in manage_attendance: {e}")

    return render_template(
        'students/manage_attendance_students.html',
        username=username,
        role=role,
        enrolled_subjects=enrolled_subjects_data
    )


@attendance_bp.route('/detail/<int:subject_id>')
@login_required
def attendance_detail(subject_id):
    """
    특정 과목의 주차별 출석 상세 내역을 표시합니다.
    학기 전체 기간에 대한 주차별 출석 현황을 보여줍니다.
    
    Args:
        subject_id: 과목 ID
    """
    username = session.get('username', '학생')
    role = session.get('role', 'student')
    student_number = session.get('student_number')

    # 학생이 아닌 경우 접근 제한
    if role != 'student':
        flash("학생만 출석 상세 내역을 이용할 수 있습니다.", "error")
        return redirect(url_for('main.index'))

    # 세션에 학번이 없으면 로그인 페이지로 리다이렉트
    if not student_number:
        flash("로그인 정보가 없습니다.", "error")
        return redirect(url_for('auth.login'))

    student_id = None
    subject_name = "알 수 없는 과목"
    attendance_records = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 학생 ID 조회
                cursor.execute("SELECT student_id FROM student WHERE student_number = %s", (student_number,))
                student_result = cursor.fetchone()
                # 학생 정보가 없으면 로그인 페이지로 리다이렉트
                if not student_result:
                    flash("학생 정보를 찾을 수 없습니다.", "error")
                    return redirect(url_for('auth.login'))
                student_id = student_result['student_id']

                # 과목 정보를 가져온다 (이름, 연도, 학기)
                cursor.execute("""
                    SELECT name, subject_year, subject_semester 
                    FROM subject 
                    WHERE subject_id = %s
                """, (subject_id,))
                subject_result = cursor.fetchone()
                if not subject_result:
                    flash("과목 정보를 찾을 수 없습니다.", "error")
                    return redirect(url_for('attendance.manage_attendance'))
                
                subject_name = subject_result['name']
                subject_year = subject_result['subject_year']
                subject_semester = subject_result['subject_semester']

                # 학기 정보에 따라 시작일과 종료일 설정
                if subject_semester == 1:
                    # 1학기: 3월 1일 ~ 6월 30일
                    semester_start = datetime(subject_year, 3, 1).date()
                    semester_end = datetime(subject_year, 6, 30).date()
                elif subject_semester == 2:
                    # 2학기: 9월 1일 ~ 12월 31일
                    semester_start = datetime(subject_year, 9, 1).date()
                    semester_end = datetime(subject_year, 12, 31).date()
                # 잘못된 학기 값인 경우 에러 처리
                else:
                    flash("올바르지 않은 학기 정보입니다.", "error")
                    return redirect(url_for('attendance.manage_attendance'))

                # 과목의 수업 스케줄 정보 가져오기 (요일, 시간)
                cursor.execute("""
                    SELECT schedule_id, day_of_week, start_time, end_time
                    FROM subject_schedule
                    WHERE subject_id = %s
                    ORDER BY 
                        FIELD(day_of_week, 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'),
                        start_time
                """, (subject_id,))
                schedules = cursor.fetchall()

                # 스케줄이 없으면 에러 처리
                if not schedules:
                    flash("과목의 수업 스케줄이 없습니다.", "error")
                    return redirect(url_for('attendance.manage_attendance'))

                # 모든 수업 세션을 날짜별로 매핑
                cursor.execute("""
                    SELECT cs.session_id, cs.class_date, cs.is_cancelled,
                           ss.schedule_id, ss.start_time, ss.end_time, ss.day_of_week
                    FROM class_session cs
                    JOIN subject_schedule ss ON cs.schedule_id = ss.schedule_id
                    WHERE ss.subject_id = %s
                """, (subject_id,))
                all_sessions = cursor.fetchall()
                
                # 세션을 날짜와 스케줄 ID로 매핑
                session_map = {}
                for session_data in all_sessions:
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

                # 요일 문자열을 숫자로 매핑 (Python weekday: 0=월요일, 6=일요일)
                weekday_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
                
                # 주차별 출석 기록 리스트 초기화
                attendance_records = []
                current_date = semester_start
                today = datetime.now().date()
                
                # 각 스케줄의 첫 번째 수업 날짜 계산
                first_week_dates = {}
                for schedule in schedules:
                    day_of_week = weekday_map[schedule['day_of_week']]
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

                # 최대 16주차까지 반복 (일반적인 학기 길이)
                for week in range(1, 17):
                    # 각 스케줄에 대해 주차별 날짜 계산
                    for schedule in schedules:
                        schedule_id = schedule['schedule_id']
                        first_date = first_week_dates[schedule_id]
                        # 해당 주차의 수업 날짜 계산
                        week_date = first_date + timedelta(weeks=week - 1)
                        
                        # 학기 종료일을 넘어가면 해당 주차는 건너뜀
                        if week_date > semester_end:
                            continue
                        
                        # 해당 날짜와 스케줄 ID로 세션 정보 조회
                        session_key = (week_date, schedule_id)
                        session_info = session_map.get(session_key)
                        
                        # 기본 상태는 '기간 아님' (수업이 없는 주차)
                        status = '기간 아님'
                        status_class = 'not-period'
                        
                        # 세션이 존재하는 경우
                        if session_info:
                            session_id = session_info['session_id']
                            
                            # 휴강인 경우
                            if session_info['is_cancelled']:
                                status = '휴강'
                                status_class = 'cancelled'
                            # 아직 날짜가 도래하지 않은 미래의 수업인 경우
                            elif week_date > today:
                                status = '기간 아님'
                                status_class = 'not-period'
                            # 오늘 또는 과거의 정상 수업인 경우 출석 기록 확인
                            else:
                                cursor.execute(
                                    "SELECT status FROM checkin WHERE session_id = %s AND student_id = %s",
                                    (session_id, student_id)
                                )
                                checkin_result = cursor.fetchone()
                                # 출결 기록이 있으면 해당 상태로 표시
                                if checkin_result:
                                    status = {
                                        'PRESENT': '출석',
                                        'LATE': '지각',
                                        'ABSENT': '결석'
                                    }.get(checkin_result['status'], '알 수 없음')
                                    status_class = checkin_result['status'].lower()
                                # 출결 기록이 없으면 '미출석'으로 처리
                                # (위에서 미래 수업은 이미 '기간 아님'으로 처리했으므로,
                                # 이 경우는 과거 수업에 출결 기록이 없는 경우임)
                                else:
                                    status = '미출석'
                                    status_class = 'absent'
                            
                            # 세션 정보에서 시간 가져오기
                            start_time = session_info['start_time']
                            end_time = session_info['end_time']
                        # 세션이 없는 경우 스케줄 기본 시간 사용
                        else:
                            start_time = schedule['start_time']
                            end_time = schedule['end_time']
                        
                        # 시간 값을 문자열로 변환 (다양한 형식 지원)
                        if isinstance(start_time, timedelta):
                            total_seconds = int(start_time.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            start_time_str = f"{hours:02d}:{minutes:02d}"
                        elif isinstance(start_time, str):
                            start_time_str = start_time[:5]
                        else:
                            start_time_str = start_time.strftime("%H:%M")
                        
                        # 종료 시간도 동일하게 변환
                        if isinstance(end_time, timedelta):
                            total_seconds = int(end_time.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            end_time_str = f"{hours:02d}:{minutes:02d}"
                        elif isinstance(end_time, str):
                            end_time_str = end_time[:5]
                        else:
                            end_time_str = end_time.strftime("%H:%M")
                        
                        attendance_records.append({
                            'week': week,
                            'class_date': week_date.strftime("%Y-%m-%d"),
                            'day_of_week': schedule['day_of_week'],
                            'start_time': start_time_str,
                            'end_time': end_time_str,
                            'status': status,
                            'status_class': status_class
                        })

    except Exception as e:
        # 사용자에게는 일반적인 에러 메시지만 표시
        flash(f"데이터베이스 오류가 발생했습니다.", "error")
        # 개발 환경에서만 상세 에러 로그 출력
        import os
        if os.getenv('FLASK_ENV') == 'development':
            print(f"Error in attendance_detail: {e}")

    return render_template(
        'students/attendance_detail.html',
        username=username,
        role=role,
        subject_name=subject_name,
        attendance_records=attendance_records
    )
