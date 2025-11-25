from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.db_helpers import get_db_connection
from mysql.connector import Error

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    사용자 로그인을 처리합니다.
    GET 요청 시 로그인 페이지를 표시하고, POST 요청 시 로그인을 처리합니다.
    """
    # POST 요청인 경우 로그인 처리
    if request.method == 'POST':
        role = request.form.get('role')  # 'student' or 'professor'
        user_id = request.form.get('user_id')

        try:
            with get_db_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # 역할에 따라 다른 쿼리 실행
                    if role == 'student':
                        # 학생 로그인: 학번으로 조회
                        cursor.execute("""
                            SELECT student_id AS id, name, student_number, 'student' AS role
                            FROM student
                            WHERE student_number = %s
                        """, (user_id,))
                    elif role == 'professor':
                        # 교수 로그인: 이메일로 조회
                        cursor.execute("""
                            SELECT professor_id AS id, name, 'professor' AS role
                            FROM professor
                            WHERE email = %s
                        """, (user_id,))
                    # 잘못된 역할인 경우 에러 처리
                    else:
                        return render_template('login.html', error="잘못된 접근입니다.")

                    user = cursor.fetchone()

                    # 사용자 정보가 있으면 로그인 성공 처리
                    if user:
                        # 세션에 로그인 정보 저장
                        session['logged_in'] = True
                        session['username'] = user['name']
                        session['user_id'] = user['id']
                        session['role'] = user['role']
                        # 학생인 경우 학번도 세션에 저장
                        if role == 'student':
                            session['student_number'] = user['student_number']
                        return redirect(url_for('main.root'))
                    # 사용자 정보가 없으면 로그인 실패
                    else:
                        return render_template('login.html', error="등록되지 않은 사용자입니다.")

        except Error as e:
            # 데이터베이스 연결 오류 처리
            print("DB 연결 오류:", e)
            return render_template('login.html', error="데이터베이스 연결 오류 발생")

    # GET 요청인 경우 로그인 페이지 표시
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    사용자 로그아웃을 처리합니다.
    세션을 초기화하고 로그인 페이지로 리다이렉트합니다.
    """
    session.clear()
    return redirect(url_for('auth.login'))
