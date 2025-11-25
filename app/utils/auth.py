"""
인증 관련 유틸리티 함수들
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from app.utils.db_helpers import get_db_connection


def login_required(f):
    """
    로그인 확인 데코레이터입니다.
    로그인되지 않은 사용자는 로그인 페이지로 리다이렉트합니다.
    
    사용법:
        @login_required
        def my_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 세션에 로그인 정보가 없거나 False인 경우
        if 'logged_in' not in session or not session.get('logged_in'):
            flash("로그인이 필요합니다.")
            return redirect(url_for('auth.login'))
        # 로그인된 경우 원래 함수 실행
        return f(*args, **kwargs)
    return decorated_function


def login_user(student_number):
    """
    학생 학번으로 로그인을 확인합니다.
    
    Args:
        student_number: 학생 학번
        
    Returns:
        bool: 로그인 성공 여부
    """
    try: 
        student_number = student_number.strip()  # 앞뒤 공백 제거
        print(f"로그인 요청 받음 (repr): {repr(student_number)}")  # 디버깅을 위한 출력
        
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT student_number FROM student WHERE student_number = %s", (student_number,))
                result = cursor.fetchone()
                
                if result:
                    db_student_number = result['student_number']
                    print(f"로그인 성공 (DB 학번 repr): {repr(db_student_number)}") 
                else:
                    print(f"로그인 실패")
                    
                return result is not None
    except Exception as e:
        print(f"Login error: {e}")
        return False