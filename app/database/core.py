
# 데이터베이스 연결 및 핵심(생성, 읽기, 수정, 삭제) 함수들을 관리함.

import pymysql.cursors
from app import config
from . import models

# 애플리케이션 전체에서 공유될 데이터베이스 연결 객체임.
db_connection = None

async def connect_to_db():
    """애플리케이션 시작 시 데이터베이스에 연결함."""
    global db_connection
    db_connection = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

async def close_db_connection():
    """애플리케이션 종료 시 데이터베이스 연결을 해제함."""
    global db_connection
    if db_connection:
        db_connection.close()
        db_connection = None

async def get_db_connection():
    """
    FastAPI의 의존성 주입 시스템을 통해 각 API 요청마다 DB 연결 객체를 제공함.
    yield 키워드를 사용하여 요청 처리 동안 연결을 유지하고, 처리가 끝나면 제어권을 돌려줌.
    """
    if db_connection is None:
        await connect_to_db()
    yield db_connection

async def init_tables():
    """models.py에 정의된 모든 테이블들을 데이터베이스에 생성함."""
    db_conn = await get_db_connection().__anext__()
    with db_conn.cursor() as cursor:
        for create_query in models.CREATE_TABLE_QUERIES:
            cursor.execute(create_query)
    db_conn.commit()

async def get_db_schema():
    """현재 데이터베이스에 생성된 모든 테이블의 구조를 조회하여 반환함."""
    db_conn = await get_db_connection().__anext__()
    schema_info = {}
    with db_conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table_row in tables:
            table_name = list(table_row.values())[0]
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            schema_info[table_name] = columns
    return schema_info

async def create_user(db_conn, username: str, hashed_password: str, email: str):
    """
    새로운 사용자 정보를 받아 users 테이블에 삽입함.
    - db_conn: 데이터베이스 연결 객체임.
    - username, hashed_password, email: 저장할 사용자 정보임.
    - 반환값: 성공 시 생성된 사용자 정보를 담은 딕셔너리, 실패(중복) 시 None임.
    """
    insert_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(insert_sql, (username, hashed_password, email))
            new_user_id = cursor.lastrowid
        db_conn.commit()
        return {"id": new_user_id, "username": username, "email": email}
    except pymysql.err.IntegrityError:
        return None