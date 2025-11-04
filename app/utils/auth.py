from functools import wraps
from flask import session, redirect, url_for, flash

#로그인 확인 로직 데코레이터 필요 시 @login_required를 추가하여 사용
def login_required(f): 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('logged_in'):
            flash("로그인이 필요합니다.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function