"""
채팅 관련 API 엔드포인트들을 정의하는 라우터 파일임.
Gemini API 테스트 등의 기능을 담당함.
"""
from fastapi import APIRouter
from app.api import gemini
from app.database import schemas

# APIRouter 객체를 생성하여 API 경로들을 그룹화함.
chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat API"]
)

@chat_router.post("/test-gemini")
async def test_gemini_endpoint(
    prompt_payload: schemas.ChatPrompt
):
    """
    Gemini API와 통신을 테스트하는 API임.
    - prompt_payload: Pydantic 모델(schemas.ChatPrompt)로, 요청 Body의 데이터가 검증됨.
    """
    user_prompt = prompt_payload.prompt
    if not user_prompt:
        return {"error": "프롬프트를 입력해야 합니다."}
        
    # gemini.py 모듈의 함수를 호출하여 AI의 응답을 받아옴.
    ai_response_text = await gemini.get_gemini_response(user_prompt)
    
    # 사용자의 질문과 AI의 답변을 함께 묶어 반환함.
    return {
        "your_prompt": user_prompt,
        "gemini_response": ai_response_text
    }