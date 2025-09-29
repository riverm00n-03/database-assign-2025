
# Gemini API와의 통신 관련된 건 여기에 작성하면 됨.

import os
import google.generativeai as genai
from fastapi import HTTPException

# .env 파일에 저장된 API 키를 가져와 Gemini 클라이언트를 설정함.
try:
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        print("경고: GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
    genai.configure(api_key=google_api_key)
except Exception as e:
    print(f"Gemini API 키 설정 중 오류 발생: {e}")

async def get_gemini_response(prompt_text: str) -> str:
    """
    주어진 텍스트 프롬프트를 Gemini API로 보내고 AI의 응답을 받아옴.
    - prompt_text: AI에게 전달할 질문 또는 메시지 문자열임.
    - 반환값: AI가 생성한 응답 텍스트 문자열임.
    """
    try:
        # 사용할 AI 모델을 지정함.
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 비동기 방식으로 API에 콘텐츠 생성을 요청함.
        response = await model.generate_content_async(prompt_text)
        
        return response.text
    except Exception as e:
        # API 통신 중 문제가 발생하면 서버 로그에 에러를 출력하고,
        # 클라이언트에게는 500번 상태 코드와 함께 에러 메시지를 전달함.
        print(f"Gemini API 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail="AI 모델 응답 생성에 실패했습니다.")