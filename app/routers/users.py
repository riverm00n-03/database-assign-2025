"""
사용자 관련 API 엔드포인트(URL 경로)들을 정의하는 라우터 파일임.
회원가입, 로그인 등의 기능을 담당함.
"""
from fastapi import APIRouter, Depends, HTTPException
from werkzeug.security import generate_password_hash 
from app.database import core as db_core
from app.database import schemas

# APIRouter 객체를 생성하여 API 경로들을 그룹화함.
# prefix="/users": 이 파일의 모든 API 경로는 '/users'로 시작함.
# tags=["User API"]: API 문서에서 'User API'라는 그룹으로 묶여 표시됨.
user_router = APIRouter(
    prefix="/users",
    tags=["User API"]
) # docs에서만 보임. 실제 경로는 /users/register. 사용자한텐 딱히 필요 없음.

@user_router.post("/register", status_code=201) 
async def register_user(
    user_data: schemas.UserCreate, 
    db_conn=Depends(db_core.get_db_connection) # 의존성 주입을 통해 DB 연결 객체를 얻음. 의존성 주입 : 함수의 매개변수에 Depends를 사용하여 다른 함수의 반환값을 자동으로 주입받는 FastAPI의 기능임.
): # 이 부분은 나도 gemini 참고함. 좀 더 쉽게 코드를 짜도 될 거 같은데.
    """
    사용자 회원가입을 처리하는 API임.
    - user_data: Pydantic 모델이고, 아이디, 비밀번호, 이메일 등의 필드를 포함함.
    """
    # werkzeug 라이브러리를 사용해 사용자 비밀번호를 안전하게 해시 처리함. 
    hashed_password = generate_password_hash(user_data.password)
    
    # DB core 모듈의 함수를 호출하여 사용자 정보를 데이터베이스에 생성함.
    created_user = await db_core.create_user(
        db_conn=db_conn,
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email
    )

    # 사용자 생성에 실패하면(아이디/이메일 중복 등), 409 에러를 발생시킴.
    if not created_user:
        raise HTTPException(
            status_code=409,
            detail="이미 존재하는 아이디 또는 이메일입니다."
        )

    # 성공 시 생성된 사용자 정보를 반환함.
    return created_user

@user_router.post("/login")
async def login_user(
    login_data: schemas.UserLogin,
    db_conn=Depends(db_core.get_db_connection)
):
    """
    사용자 로그인 처리를 담당하는 API임.
    - login_data: Pydantic 모델이고, 아이디와 비밀번호 필드를 포함함.
    """
    # 사용자의 정보를 조회부터
    user_record = await db_core.verify_password(
        db_conn=db_conn,
        username=login_data.username
    ) # user_record : 사용자의 정보가 담긴 딕셔너리 또는 None
    if not user_record: # 사용자의 정보가 없는 경우
        raise HTTPException(
            status_code=404,
            detail="사용자를 찾을 수 없습니다."
        )
    # 사용자의 비밀번호가 일치하는지 확인함.
    if not db_core.verify_password(
        plain_password=login_data.password,
        hashed_password=user_record['hashed_password']
    ):
        raise HTTPException(
            status_code=401,
            detail="비밀번호가 올바르지 않습니다."
        )
    # 로그인 성공 시 사용자 정보를 반환함.
    return {
        "message": "로그인 성공",
        "user": {
            "id": user_record['id'],
            "username": user_record['username'],
            "email": user_record['email']
        }
    }

    