
#메인 파일임. FastAPI 앱을 설정하고, 라우터들을 포함하며, 시작/종료 이벤트를 처리함.
from fastapi import FastAPI
from .database import core as db_core
from .routers import users, chat

from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
import os

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