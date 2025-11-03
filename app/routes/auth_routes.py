from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.login import login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST']) # /auth/login 라우터
def login():
    if request.method == 'POST': # POST 요청 시
        student_number = request.form['student_number']
        print(f"Received form data: {request.form}") # 디버깅을 위한 출력
        if login_user(student_number): # login_user 함수 호출
            session['logged_in'] = True
            session['username'] = student_number # 사용자 이름 설정
            return redirect(url_for('main.root')) # 메인 앱의 index(혹은 루트)로 리다이렉트
        else:
            return render_template('login.html', error='존재하지 않는 학번입니다.') # login.html 템플릿 렌더링
    return render_template('login.html') # login.html 템플릿 렌더링

@auth_bp.route('/logout') # /auth/logout 라우터
def logout():
    session.pop('logged_in', None) # 로그인 상태 제거   
    session.pop('username', None) # 사용자 이름 제거
    return redirect(url_for('auth.login')) # 로그인 페이지로 리다이렉트