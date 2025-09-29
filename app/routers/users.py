"""
사용자 관련 API 엔드포인트(URL 경로)들을 정의하는 라우터 파일임.
회원가입, 로그인 등의 기능을 담당함.
"""
from fastapi import APIRouter, Depends, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import core as db_core
from app.database import schemas

# APIRouter 객체를 생성하여 API 경로들을 그룹화함.
# prefix="/users": 이 파일의 모든 API 경로는 '/users'로 시작함.
# tags=["User API"]: API 문서에서 'User API'라는 그룹으로 묶여 표시됨.
user_router = APIRouter(
    prefix="/users",
    tags=["User API"]
)

@user_router.post("/register", status_code=201)
async def register_user(
    user_data: schemas.UserCreate,
    db_conn=Depends(db_core.get_db_connection)
):
    """
    사용자 회원가입을 처리하는 API 엔드포인트.

    - **user_data**: Pydantic 모델(`schemas.UserCreate`)을 통해 요청 본문(body)의 유효성을 검사합니다.
                   사용자 이름, 비밀번호, 이메일을 포함해야 합니다.
    - **db_conn**: `Depends(db_core.get_db_connection)`를 통해 FastAPI의 의존성 주입 기능을 사용하여
                   각 요청마다 데이터베이스 연결 객체를 자동으로 얻습니다.
    """
    # 1. 비밀번호 해싱
    # werkzeug 라이브러리의 generate_password_hash 함수를 사용하여
    # 사용자 비밀번호를 안전한 해시 값으로 변환합니다.
    # 원본 비밀번호를 직접 저장하는 것은 매우 위험합니다.
    hashed_password = generate_password_hash(user_data.password)

    # 2. 데이터베이스에 사용자 생성 요청
    # `db_core.create_user` 함수를 호출하여 해시된 비밀번호와 함께 사용자 정보를 데이터베이스에 저장합니다.
    created_user = await db_core.create_user(
        db_conn=db_conn,
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email
    )

    # 3. 결과 처리
    # `create_user` 함수는 사용자 생성 실패 시(예: 사용자 이름 또는 이메일 중복) None을 반환합니다.
    # 이 경우, 409 Conflict 상태 코드와 함께 에러 메시지를 클라이언트에게 보냅니다.
    if not created_user:
        raise HTTPException(
            status_code=409,
            detail="이미 존재하는 아이디 또는 이메일입니다."
        )

    # 4. 성공 응답
    # 사용자 생성이 성공하면, 생성된 사용자 정보(ID, 사용자 이름, 이메일)를
    # HTTP 상태 코드 201(Created)과 함께 반환합니다.
    return created_user

    