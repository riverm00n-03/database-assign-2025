from functools import wraps
from flask import session, redirect, url_for, flash


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