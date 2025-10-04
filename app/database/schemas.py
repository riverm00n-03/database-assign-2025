"""
Pydantic 모델(스키마)을 정의하는 파일임.
API의 요청(Request) 및 응답(Response) 데이터 형식을 지정하고,
자동으로 데이터 유효성을 검사하는 역할을 함.
"""
from pydantic import BaseModel

class UserCreate(BaseModel):
    """회원가입 API 요청 시 Body에 담길 데이터의 형식을 정의함."""
    username: str
    password: str
    email: str

class ChatPrompt(BaseModel):
    """채팅 API 요청 시 Body에 담길 데이터의 형식을 정의함."""
    prompt: str

class UserLogin(BaseModel):
    """로그인 API 요청 시 Body에 담길 데이터의 형식을 정의함."""
    username: str
    password: str
class StoryBase(BaseModel):
    title: str
    prompt: str
    category: str

class StoryCreate(StoryBase):
    creator_id: int

class Story(StoryBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True # DB 모델 객체를 Pydantic 모델로 자동 변환
class UserSessionCreate(BaseModel):
    """채팅방 생성 또는 삭제 요청 시 필요한 사용자 ID"""
    user_id: int