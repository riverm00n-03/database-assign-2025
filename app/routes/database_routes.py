from flask import Blueprint, jsonify, render_template
from mysql.connector import connect
import datetime
from config import DB_CONFIG

db_bp = Blueprint('database', __name__)


@db_bp.route('/show_database')
def show_database():
    """
    데이터베이스의 모든 테이블과 데이터를 JSON 형식으로 반환합니다.
    개발 및 디버깅 목적으로 사용됩니다.
    """
    db_data = {}
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 모든 테이블 목록 조회
                cursor.execute("SHOW TABLES")
                tables = [row['Tables_in_wcheck'] for row in cursor.fetchall()]

                # 각 테이블의 데이터 조회 및 처리
                for table_name in tables:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    processed_rows = []
                    # 각 행의 데이터 타입에 따라 변환 처리
                    for row in rows:
                        processed_row = {}
                        for key, value in row.items():
                            # 날짜/시간 객체인 경우 ISO 형식으로 변환
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                processed_row[key] = value.isoformat()
                            # timedelta 객체인 경우 HH:MM:SS 형식으로 변환
                            elif isinstance(value, datetime.timedelta):
                                total_seconds = int(value.total_seconds())
                                hours = total_seconds // 3600
                                minutes = (total_seconds % 3600) // 60
                                seconds = total_seconds % 60
                                processed_row[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            # time 객체인 경우 ISO 형식으로 변환
                            elif isinstance(value, datetime.time):
                                processed_row[key] = value.isoformat()
                            # 기타 타입은 그대로 저장
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        # 에러 발생 시 JSON 에러 응답 반환
        return jsonify({"error": str(e)}), 500
    return jsonify(db_data)


@db_bp.route('/')
def show_database_html():
    """
    데이터베이스의 모든 테이블과 데이터를 HTML 페이지로 표시합니다.
    개발 및 디버깅 목적으로 사용됩니다.
    """
    db_data = {}
    tables = []
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                # 데이터베이스 선택
                cursor.execute("USE wcheck")
                # 모든 테이블 목록 조회
                cursor.execute("SHOW TABLES")
                tables = [row['Tables_in_wcheck'] for row in cursor.fetchall()]

                # 각 테이블의 데이터 조회 및 처리
                for table_name in tables:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    processed_rows = []
                    # 각 행의 데이터 타입에 따라 변환 처리
                    for row in rows:
                        processed_row = {}
                        for key, value in row.items():
                            # 날짜/시간 객체인 경우 ISO 형식으로 변환
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                processed_row[key] = value.isoformat()
                            # timedelta 객체인 경우 HH:MM:SS 형식으로 변환
                            elif isinstance(value, datetime.timedelta):
                                total_seconds = int(value.total_seconds())
                                hours = total_seconds // 3600
                                minutes = (total_seconds % 3600) // 60
                                seconds = total_seconds % 60
                                processed_row[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            # time 객체인 경우 ISO 형식으로 변환
                            elif isinstance(value, datetime.time):
                                processed_row[key] = value.isoformat()
                            # 기타 타입은 그대로 저장
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        # 에러 발생 시 에러 메시지와 함께 빈 데이터 반환
        return render_template('db.html', tables=[], db_data={}, error=str(e))
    return render_template('db.html', tables=tables, db_data=db_data)
