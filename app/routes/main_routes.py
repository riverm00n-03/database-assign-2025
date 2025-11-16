from flask import Blueprint, render_template, redirect, url_for, session
from app.utils.auth import login_required


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def root():
    """
    메인 페이지를 표시합니다.
    로그인된 사용자의 홈 화면을 보여줍니다.
    """
    # 세션에서 사용자 정보 가져오기
    username = session.get('username', '사용자')
    role = session.get('role', 'student')

    return render_template('index.html', username=username, role=role)
