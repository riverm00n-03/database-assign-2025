from flask import Blueprint, render_template, redirect, url_for, session
from app.utils.auth import login_required


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required # 로그인 되어있는 동안만 동작
def root():
    # 로그인된 사용자 이름과 역할 전달 (UI 표시용)
    username = session.get('username', '사용자')
    role = session.get('role', 'student')

    return render_template('index.html', username=username, role=role)
