from flask import Blueprint, render_template, redirect, url_for, session
from app.utils.auth import login_required
from app.utils.db_helpers import get_db_connection, get_student_id_by_number, format_time_to_str, to_time
from app.utils.session_helpers import get_session_info
from app.utils.constants import WEEKDAY_TO_STR
from datetime import datetime


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def root():
    """
    메인 페이지를 표시합니다.
    로그인된 사용자의 홈 화면을 보여줍니다.
    """
    # 세션에서 사용자 정보 가져오기
    session_info = get_session_info()
    username = session_info['username']
    role = session_info['role']
    student_number = session_info['student_number']
    
    today_classes = []
    
    # 오늘의 과목 조회 (학생만)
    if role == 'student':
        try:
            server_now = datetime.now()
            today_index = server_now.weekday()
            
            # 주말이 아니면 오늘의 과목 조회
            if today_index <= 4:
                today_weekday = WEEKDAY_TO_STR.get(today_index)
                
                with get_db_connection() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        student_id = get_student_id_by_number(cursor, student_number)
                        
                        if student_id:
                            # 오늘 수업 스케줄 조회
                            cursor.execute("""
                                SELECT ss.schedule_id, s.name AS subject_name, p.name AS professor_name,
                                       ss.location, ss.start_time, ss.end_time, s.subject_id
                                FROM subject_schedule ss
                                JOIN subject s ON ss.subject_id = s.subject_id
                                LEFT JOIN professor p ON s.professor_id = p.professor_id
                                JOIN enrollment e ON e.subject_id = s.subject_id
                                WHERE UPPER(ss.day_of_week) = %s
                                  AND e.student_id = %s
                                ORDER BY ss.start_time
                            """, (today_weekday.upper(), student_id))
                            rows = cursor.fetchall()
                            
                            for row in rows:
                                row['start_time'] = to_time(row['start_time'])
                                row['end_time'] = to_time(row['end_time'])
                                
                                today_classes.append({
                                    'subject_name': row['subject_name'],
                                    'professor_name': row['professor_name'] or '-',
                                    'location': row['location'] or '-',
                                    'start_time_str': format_time_to_str(row['start_time']),
                                    'end_time_str': format_time_to_str(row['end_time'])
                                })
        except Exception as e:
            # 에러 발생 시 빈 리스트 유지
            import os
            if os.getenv('FLASK_ENV') == 'development':
                print(f"Error in root: {e}")

    return render_template('index.html', username=username, role=role, current_page='', today_classes=today_classes)
