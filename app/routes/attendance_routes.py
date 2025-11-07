from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
@login_required
def show_attendance():
    username = session.get('username', '학생')
    role = session.get('role', 'student')  # ✅ 여기가 핵심
    server_now = datetime.now()

    return render_template(
        'attendance_check.html',
        username=username,
        role=role,
        server_now_iso=server_now.isoformat(),
        server_now_fmt=server_now.strftime("%Y-%m-%d %H:%M:%S"),
        today_classes=[]
    )
