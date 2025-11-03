from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    # 로그인 안 된 경우 로그인 페이지로 리다이렉트
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))

    # 로그인된 사용자 이름과 역할 전달 (UI 표시용)
    username = session.get('username', '사용자')
    role = session.get('role', 'student')

    return render_template('index.html', username=username, role=role)
