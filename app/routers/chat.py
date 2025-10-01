"""
채팅 관련 API 엔드포인트들을 정의하는 라우터 파일임.
Gemini API 테스트 등의 기능을 담당함.
"""
from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection
from app.api import gemini
from app.database import schemas
from app.database import core as db_core

# APIRouter 객체를 생성하여 API 경로들을 그룹화함.
chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat API"]
)

@chat_router.post("/new/{story_id}", response_model=schemas.SessionInfo, description="새로운 채팅방을 생성합니다.")
async def create_new_chat_session(
    story_id: int,
    user_info: schemas.UserIdentifier,
    db_conn: Connection = Depends(db_core.get_db_connection)
):
    """
    특정 story와 사용자를 위한 새로운 채팅 세션(채팅방)을 생성하고,
    생성된 채팅방의 ID (session_id)를 반환합니다.
    """
    session_id = await db_core.create_session(db_conn, user_info.user_id, story_id)
    if not session_id:
        raise HTTPException(status_code=500, detail="채팅방을 생성하지 못했습니다.")
    
    return {"session_id": session_id}


@chat_router.post("/{session_id}", response_model=schemas.ChatMessage, description="기존 채팅방에서 메시지를 주고받습니다.")
async def post_chat_message(
    session_id: int,
    prompt: schemas.ChatPrompt,
    db_conn: Connection = Depends(db_core.get_db_connection)
):
    """
    사용자의 메시지를 DB에 저장하고, 과거 대화 기록을 바탕으로 AI의 답변을 생성하여 반환합니다.
    """
    # 1. 사용자의 메시지를 history 테이블에 저장
    await db_core.add_message_to_history(db_conn, session_id, 'user', prompt.prompt)
    
    # 2. 과거 대화 기록을 DB에서 모두 가져옴
    past_conversations = await db_core.get_history_by_session(db_conn, session_id)
    
    # 3. 과거 기록과 새 메시지를 합쳐 AI에게 보낼 최종 프롬프트 생성
    full_prompt = ""
    for conv in past_conversations:
        full_prompt += f"{conv['sender']}: {conv['message']}\n"
    
    # 4. gemini.py의 함수를 호출하여 AI 답변 생성
    ai_message = await gemini.get_gemini_response(full_prompt)
    
    # 5. AI의 답변을 history 테이블에 저장
    await db_core.add_message_to_history(db_conn, session_id, 'bot', ai_message)
    
    # 6. AI의 답변을 사용자에게 반환
    return {"sender": "bot", "message": ai_message}