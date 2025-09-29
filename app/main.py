#메인 파일임. FastAPI 앱을 설정하고, 라우터들을 포함하며, 시작/종료 이벤트를 처리함.
from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from werkzeug.security import check_password_hash
import os
from urllib.parse import parse_qs

from . import config
from .database import core as db_core
from .routers import users, chat

# 현재 파일(__file__)의 디렉토리 경로를 가져옵니다. (frontend 폴더 경로를 찾기 위함)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 프로젝트 루트 폴더에 있는 frontend 폴더의 경로를 설정합니다.
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

# FastAPI 앱 인스턴스를 생성하고, API 문서에 표시될 제목, 설명, 버전을 설정함.
app = FastAPI(
    title="Character Chat API",
    description="Gemini AI 모델을 이용한 캐릭터 챗 서비스 API",
    version="0.1.0"
)

# FastAPI의 이벤트 핸들러를 사용하여 앱 시작/종료 시 특정 함수를 실행함.
@app.on_event("startup")
async def on_startup():
    #서버가 시작될 때 데이터베이스에 연결함
    await db_core.connect_to_db()

@app.on_event("shutdown")
async def on_shutdown():
    #서버가 종료될 때 데이터베이스 연결을 해제함
    await db_core.close_db_connection()


# 기능별로 분리된 라우터들을 메인 앱에 포함시킴.
app.include_router(users.user_router)
app.include_router(chat.chat_router)

# /static 이라는 URL 경로로 접속하면, 실제 FRONTEND_DIR(/frontend) 폴더의 파일들을 보여줄 수 있게 됨.
# 예: /static/index.html, /static/css/style.css
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# 라우터들

@app.get("/", tags=["Default"])
def root():
    #서버의 루트 경로로, 간단한 환영 메시지를 반환함.
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))


# 데이터베이스 관련 라우터들
@app.get("/init-db", tags=["Database"])
async def init_db_route():
    #DB에 테이블들을 일괄 생성하는 유틸리티 API임.
    try:
        await db_core.init_tables()
        return {"status": "success", "message": "DB 잘 만들어짐."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/check-db", tags=["Database"])
async def check_db_schema_route():
    #생성된 DB 테이블들의 구조를 확인함.
    try:
        schema_info = await db_core.get_db_schema()
        return schema_info
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/check-db-html", tags=["Database"])
def db_schema_view_route():
    # DB 스키마 정보를 보여주는 HTML 페이지를 반환함.
    db_html_path = os.path.join(FRONTEND_DIR, 'db.html')
    if not os.path.exists(db_html_path):
        return {"error": "db.html 파일이 없음.."}
    return FileResponse(db_html_path)

@app.get("/reset-db", tags=["Database"])
async def reset_db_route():
    #DB의 모든 테이블을 삭제하고 다시 생성함.
    try:
        await db_core.reset_tables()
        return {"status": "success", "message": "DB 리셋됨."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/table-data/{table_name}", tags=["Database"])
async def get_table_data_route(table_name: str, db_conn=Depends(db_core.get_db_connection)):
    """
    특정 테이블의 모든 데이터를 조회하여 반환함.
    """
    try:
        data = await db_core.get_table_data(db_conn, table_name)
        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 회원가입 / 로그인 / 회원탈퇴 / 회원정보수정 라우터들
@app.get("/register", tags=["User"])
async def get_register_page():
    register_html_path = os.path.join(FRONTEND_DIR, 'register.html')
    if not os.path.exists(register_html_path):
        return {"error": "register.html 파일이 없음.."}
    return FileResponse(register_html_path)

@app.get("/login", tags=["User"])
async def get_login_page():
    login_html_path = os.path.join(FRONTEND_DIR, 'login.html')
    if not os.path.exists(login_html_path):
        return {"error": "login.html 파일이 없음.."}
    return FileResponse(login_html_path)

@app.post("/login", tags=["User"])
async def login_user(
    request: Request,
    db_conn=Depends(db_core.get_db_connection)
):
    """
    사용자 로그인을 처리하는 API (HTML 폼 요청 처리용)
    'python-multipart' 라이브러리 없이 폼 데이터를 수동으로 처리합니다.

    - request: FastAPI의 Request 객체. 요청의 모든 정보를 담고 있습니다.
    - db_conn: 데이터베이스 연결 의존성 주입
    """
    # 1. 원시 요청 본문(raw request body)을 읽어옵니다.
    # request.body()는 bytes 형태로 데이터를 반환합니다.
    body_bytes = await request.body()

    # 2. Bytes를 문자열로 디코딩하고, URL 인코딩된 폼 데이터를 파싱합니다.
    # 예: b'username=test&password=123' -> {'username': ['test'], 'password': ['123']}
    body_str = body_bytes.decode()
    parsed_data = parse_qs(body_str)
    
    # 3. 파싱된 데이터에서 사용자 이름과 비밀번호를 추출합니다.
    # parse_qs는 값을 리스트로 반환하므로, 첫 번째 요소를 가져옵니다.
    username = parsed_data.get('username', [None])[0]
    password = parsed_data.get('password', [None])[0]

    # 사용자 이름이나 비밀번호가 없는 경우 에러 처리
    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="사용자 이름과 비밀번호를 모두 입력해야 합니다."
        )

    # 4. 데이터베이스에서 사용자 이름으로 사용자 정보를 조회합니다.
    user_record = await db_core.get_user_by_username(
        db_conn=db_conn,
        username=username
    )

    # 5. 사용자가 존재하지 않거나 비밀번호가 일치하지 않는 경우, 에러를 발생시킵니다.
    if not user_record or not check_password_hash(user_record['password'], password):
        raise HTTPException(
            status_code=401,
            detail="사용자 이름 또는 비밀번호가 올바르지 않습니다."
        )

    # 6. 로그인 성공 시, 메인 페이지로 리디렉션합니다.
    return RedirectResponse(url="/", status_code=303)