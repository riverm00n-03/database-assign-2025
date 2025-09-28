import pymysql
import os
from flask import g
from . import models

def get_db():
    """현재 요청에 대한 DB 커넥션을 가져오거나 새로 생성합니다."""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'db'), # Docker Compose 서비스 이름
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DATABASE'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """요청이 끝나면 DB 커넥션을 닫습니다."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_tables():
    """models.py에 정의된 모든 테이블을 생성합니다."""
    db = get_db()
    with db.cursor() as cursor:
        for query in models.CREATE_TABLE_QUERIES:
            cursor.execute(query)
    db.commit()

def get_db_schema():
    """DB에 있는 모든 테이블의 구조를 조회하여 반환합니다."""
    db = get_db()
    schema = {}
    with db.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table_row in tables:
            table_name = list(table_row.values())[0]
            cursor.execute(f"DESCRIBE `{table_name}`") # 테이블 이름에 백틱 사용
            columns = cursor.fetchall()
            schema[table_name] = columns
    return schema
