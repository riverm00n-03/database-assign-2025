from flask import Blueprint, jsonify, render_template
from mysql.connector import connect
import datetime
from config import DB_CONFIG

db_bp = Blueprint('database', __name__)

@db_bp.route('/show_database') # /database/show_database 경로로 접근 시 해당 함수 실행
def show_database():
    db_data = {}
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row['Tables_in_wcheck'] for row in cursor.fetchall()]

                for table_name in tables:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    processed_rows = []
                    for row in rows:
                        processed_row = {}
                        for key, value in row.items():
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                processed_row[key] = value.isoformat()
                            elif isinstance(value, datetime.timedelta):
                                # timedelta를 문자열로 변환 (HH:MM:SS 형식)
                                total_seconds = int(value.total_seconds())
                                hours = total_seconds // 3600
                                minutes = (total_seconds % 3600) // 60
                                seconds = total_seconds % 60
                                processed_row[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            elif isinstance(value, datetime.time):
                                processed_row[key] = value.isoformat()
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(db_data)

@db_bp.route('/') # /database/ 경로로 접근 시 HTML 페이지 표시
def show_database_html():
    db_data = {}
    tables = []
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SHOW TABLES")
                tables = [row['Tables_in_wcheck'] for row in cursor.fetchall()]

                for table_name in tables:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    processed_rows = []
                    for row in rows:
                        processed_row = {}
                        for key, value in row.items():
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                processed_row[key] = value.isoformat()
                            elif isinstance(value, datetime.timedelta):
                                # timedelta를 문자열로 변환 (HH:MM:SS 형식)
                                total_seconds = int(value.total_seconds())
                                hours = total_seconds // 3600
                                minutes = (total_seconds % 3600) // 60
                                seconds = total_seconds % 60
                                processed_row[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            elif isinstance(value, datetime.time):
                                processed_row[key] = value.isoformat()
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        return render_template('db.html', tables=[], db_data={}, error=str(e))
    return render_template('db.html', tables=tables, db_data=db_data)
