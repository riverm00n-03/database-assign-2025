# 데이터베이스 연결 및 핵심(생성, 읽기, 수정, 삭제) 함수들을 관리함.

import pymysql.cursors
from app import config
from . import models

# 애플리케이션 전체에서 공유될 데이터베이스 연결 객체임.
db_connection = None


# DB 연결 관리 함수들
async def connect_to_db():
    """애플리케이션 시작 시 데이터베이스에 연결함."""
    global db_connection
    # 환경 변수(config.py)를 사용하여 MySQL에 연결합니다.
    db_connection = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        # 딕셔너리 형태로 결과를 받아오는 Cursor를 사용합니다.
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
    """
    if db_connection is None:
        await connect_to_db()
    # yield 키워드는 요청 처리 동안 연결을 유지하고, 처리가 끝나면 제어권을 돌려주는 역할을 합니다.
    yield db_connection

# DB 유틸리티 함수들 (API 요청 외부에서 호출됨)
async def init_tables():
    """
    models.py에 정의된 모든 테이블들을 데이터베이스에 생성함.
    (API 요청 외부에서 호출되므로, 전역 db_connection을 직접 사용하도록 단순화)
    """
    global db_connection
    if db_connection is None:
        await connect_to_db()

    with db_connection.cursor() as cursor:
        for create_query in models.CREATE_TABLE_QUERIES:
            # 쿼리를 실행하여 테이블을 생성함.
            cursor.execute(create_query)
    # 데이터베이스에 변경 사항을 최종 반영함.
    db_connection.commit()

async def get_db_schema():
    """
    현재 데이터베이스에 생성된 모든 테이블의 구조를 조회하여 반환함.
    (API 요청 외부에서 호출되므로, 전역 db_connection을 직접 사용하도록 단순화)
    """
    global db_connection
    if db_connection is None:
        await connect_to_db()
        
    schema_info = {}
    with db_connection.cursor() as cursor:
        # DB에 있는 모든 테이블 이름을 조회함.
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table_row in tables:
            # pymysql DictCursor가 딕셔너리로 반환하므로, 첫 번째 값(테이블 이름)을 가져옴.
            table_name = list(table_row.values())[0]
            # 각 테이블의 구조(컬럼 정보)를 조회함.
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            schema_info[table_name] = columns
    return schema_info


# 사용자 관련 DB 핵심 함수들
async def create_user(db_conn, username: str, hashed_password: str, email: str): # db_conn을 매개변수로 받음.
    """
    새로운 사용자 정보를 받아 users 테이블에 삽입함.
    - db_conn: FastAPI Depends를 통해 받은 DB 연결 객체임.
    - 반환값: 성공 시 생성된 사용자 정보를 담은 딕셔너리, 실패(중복) 시 None임.
    """
    insert_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    try:
        with db_conn.cursor() as cursor:
            # 쿼리 실행 시 %s를 사용하여 SQL Injection 공격을 방지합니다.
            cursor.execute(insert_sql, (username, hashed_password, email))
            new_user_id = cursor.lastrowid # 삽입된 행의 ID를 가져옴.
        db_conn.commit()
        return {"id": new_user_id, "username": username, "email": email}
    # 아이디나 이메일 중복 시 발생하는 예외를 처리함.
    except pymysql.err.IntegrityError:
        return None
    
async def get_user_by_username(db_conn, username: str):
    """
    주어진 username에 해당하는 사용자의 정보를 users 테이블에서 조회함.
    - db_conn: FastAPI Depends를 통해 받은 DB 연결 객체임.
    - 반환값: 사용자가 존재하면 사용자 정보를 담은 딕셔너리, 없으면 None임.
    """
    select_sql = "SELECT id, username, password, email, is_banned, created_at FROM users WHERE username = %s"
    with db_conn.cursor() as cursor:
        cursor.execute(select_sql, (username,))
        # 하나의 결과만 가져옴. (username은 UNIQUE 제약 조건이 있으므로)
        user_record = cursor.fetchone() 
    return user_record


# 비밀번호 확인 (DB와는 직접 관련 없음)
from werkzeug.security import check_password_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 확인함.
    (routers/users.py 파일에서 사용됨)
    """
    return check_password_hash(hashed_password, plain_password)

async def reset_tables():
    # 모든 테이블을 삭제하고, 다시 생성함.
    # 그 전에, alert로 사용자에게 경고 메시지를 띄우도록 프론트엔드에 알림을 보낼 수 있음.
    global db_connection
    if db_connection is None:
        await connect_to_db()
    with db_connection.cursor() as cursor:
        # 외래 키 제약 조건 비활성화. 없으면 외래 키 제약 조건 위반으로 삭제가 안 됨.
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        # 모든 테이블을 삭제함.
        for drop_query in models.DROP_TABLE_QUERIES:
            cursor.execute(drop_query)
        # 다시 테이블을 생성함.
        for create_query in models.CREATE_TABLE_QUERIES:
            cursor.execute(create_query)
        # 외래 키 제약 조건 재활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_connection.commit()