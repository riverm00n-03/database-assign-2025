from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from mysql.connector import connect, Error
from config import DB_CONFIG

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')  # 'student' or 'professor'
        user_id = request.form.get('user_id')

        try:
            with connect(**DB_CONFIG) as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # 학생 로그인
                    if role == 'student':
                        cursor.execute("""
                            SELECT student_id AS id, name, 'student' AS role
                            FROM student
                            WHERE student_number = %s
                        """, (user_id,))
                    # 교수 로그인
                    elif role == 'professor':
                        cursor.execute("""
                            SELECT professor_id AS id, name, 'professor' AS role
                            FROM professor
                            WHERE email = %s
                        """, (user_id,))
                    else:
                        return render_template('login.html', error="잘못된 접근입니다.")

                    user = cursor.fetchone()

                    if user:
                        # 로그인 성공
                        session['logged_in'] = True
                        session['username'] = user['name']
                        session['user_id'] = user['id']
                        session['role'] = user['role']
                        return redirect(url_for('main.root'))
                    else:
                        # DB에 없음
                        return render_template('login.html', error="등록되지 않은 사용자입니다.")

        except Error as e:
            print("DB 연결 오류:", e)
            return render_template('login.html', error="데이터베이스 연결 오류 발생")

    # GET 요청 시
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
