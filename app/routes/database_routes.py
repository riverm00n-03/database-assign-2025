from flask import Blueprint, jsonify
from mysql.connector import connect
import datetime
from config import DB_CONFIG

db_bp = Blueprint('database', __name__)

@db_bp.route('/show_database')
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
                            else:
                                processed_row[key] = value
                        processed_rows.append(processed_row)
                    db_data[table_name] = processed_rows
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(db_data)
