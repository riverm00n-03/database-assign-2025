from flask import Flask, jsonify
from mysql.connector import connect
from config import DB_CONFIG

app = Flask(__name__) # Flask 애플리케이션 인스턴스 생성

@app.route('/') # 루트 경로에 접근 시 실행할 함수
def root():
    return "Hello, World!"

@app.route('/show_database') # 데이터베이스 조회 경로
def show_database():
    # wcheck 데이터베이스의 모든 테이블과 칼럼을 조회하는 함수
    db_info = {}
    try:
        with connect(**DB_CONFIG) as connection: # **가 붙은 이유 : DB_CONFIG 딕셔너리를 키워드 인자로 전달하기 위해서
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'wcheck'")
                tables = [row[0] for row in cursor.fetchall()]

                for table_name in tables:
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'wcheck' AND table_name = '{table_name}'")
                    columns = [row[0] for row in cursor.fetchall()]
                    db_info[table_name] = columns
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # 오류 발생 시의 예외 처리
    return jsonify(db_info) # 데이터베이스 정보를 JSON 형식으로 반환


if __name__ == '__main__':
    app.run(debug=True)
    