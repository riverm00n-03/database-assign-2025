from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from mysql.connector import connect
import datetime
from .config import DB_CONFIG
from .utils.login import login_user

app = Flask(__name__) # Flask 애플리케이션 인스턴스 생성
app.secret_key = 'your_secret_key' # 세션 관리를 위한 secret key 설정

@app.route('/') # 루트 경로에 접근 시 실행할 함수
def root():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/show_database') # 데이터베이스 조회 경로
def show_database():
    # wcheck 데이터베이스의 모든 테이블과 데이터를 조회하는 함수
    db_data = {}
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor: # 딕셔너리 형태로 결과를 가져오기 위해 dictionary=True 설정
                cursor.execute("SHOW TABLES")
                tables = [row['Tables_in_wcheck'] for row in cursor.fetchall()]

                for table_name in tables:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    # datetime 객체를 문자열로 변환하여 JSON 직렬화 가능하게 함
                    processed_rows = []
                    for row in rows:
                        processed_row = {}
                        for key, value in row.items():
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                processed_row[key] = value.isoformat()
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # 오류 발생 시의 예외 처리
    return jsonify(db_data) # 데이터베이스 데이터를 JSON 형식으로 반환

@app.route('/login', methods=['GET', 'POST'])
def login(): # 로그인 함수
    if request.method == 'POST':
        student_number = request.form['student_number']
        print(f"Received form data: {request.form}") # 디버깅을 위한 출력
        if login_user(student_number):
            session['logged_in'] = True
            session['username'] = student_number
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='존재하지 않는 학번입니다.')
    return render_template('login.html')

@app.route('/index')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
    